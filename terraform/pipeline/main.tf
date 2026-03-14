# S3, Glue, IAM, ECS Task
provider "aws" {
  region = "eu-west-2"
}

resource "aws_s3_bucket" "food_truck_sales" {
  bucket = "c22-jessh-food-truck-bucket"
}

# === Policies ===
# IAM policy attachment for glue crawler role
resource "aws_iam_role_policy_attachment" "glue-crawler-policy-attachment" {
  role       = aws_iam_role.glue-crawler-iam-role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}
resource "aws_iam_role_policy_attachment" "glue-crawler-s3-policy-attachment" {
  role       = aws_iam_role.glue-crawler-iam-role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}
# Task execution Policy attachment for ECS task role
resource "aws_iam_role_policy_attachment" "ecs-task-policy-attachment" {
  role       = aws_iam_role.ecs-setup-role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
# S3 and Athena access for ECS task role
resource "aws_iam_role_policy_attachment" "ecs-task-s3-policy-attachment" {
  role       = aws_iam_role.ecs-pipeline-role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}
resource "aws_iam_role_policy_attachment" "ecs-task-athena-policy-attachment" {
  role       = aws_iam_role.ecs-pipeline-role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonAthenaFullAccess"
}

# === IAM Roles ===
# IAM role for glue crawler
resource "aws_iam_role" "glue-crawler-iam-role" {
  name = "c22-jessh-glue-crawler-role"
  assume_role_policy = jsonencode({ 
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "glue.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# IAM role for ECS task - Get Pipeline ready to run on Fargate (CloudWatch logs, ECR pull, Secrets Manager, S3, Athena)
resource "aws_iam_role" "ecs-setup-role" {
  name = "c22-jessh-ecs-setup-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })  
}


# IAM role for ECS task - Run pipeline code, access secrets, S3, Athena
resource "aws_iam_role" "ecs-pipeline-role" {
  name = "c22-jessh-ecs-pipeline-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })  
}




# === Glue Database ===
resource "aws_glue_catalog_database" "food-truck-sales-db" {
  name = "c22-jessh-food-truck-sales-db"
}

# Glue Crawler
resource "aws_glue_crawler" "truck-glue-crawler" {
  database_name = aws_glue_catalog_database.food-truck-sales-db.name
  name          = "c22-jessh-glue-crawler"
  role          = aws_iam_role.glue-crawler-iam-role.arn

  s3_target {
    path = "s3://c22-jessh-food-truck-bucket"
  }
}

# === VPC & Networking ===
# Use the default VPC instead of creating a new one
data "aws_vpc" "c22-vpc" {
  id = "vpc-03f0d39570fbaa750"
}

# Get default subnets in the default VPC
data "aws_subnets" "c22-subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.c22-vpc.id]
  }
}

# Security group for ECS task (allow outbound HTTPS to reach Secrets Manager)
resource "aws_security_group" "pipeline_task_sg" {
  name   = "c22-jessh-pipeline-task-sg"
  vpc_id = data.aws_vpc.c22-vpc.id

  # Allow outbound HTTPS to reach AWS services
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # ALlow outbound MySQL to reach RDS database
  egress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow outbound on all ports (for database connections, etc.)
  egress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "c22-jessh-pipeline-task-sg"
  }
}

# === Resources for ECS Task ===
# cloud watch log group for ECS task
resource "aws_cloudwatch_log_group" "pipeline" {
  name = "/ecs/c22-jessh-etl-ecr"
}
# ECR repository for pipeline container image
resource "aws_ecr_repository" "pipeline" {
  name = "c22-jessh-etl-ecr"
}

# # ECS cluster for pipeline
# resource "aws_ecs_cluster" "pipeline" {
#   name = "c22-jessh-etl-cluster"
# }

# ECS Cluster for pipeline
resource "aws_ecs_cluster" "pipeline" {
  name = "c22-jessh-etl-cluster"
}

# ECS Service to run the task with proper network config
resource "aws_ecs_service" "pipeline" {
  name            = "c22-jessh-etl-service"
  cluster         = aws_ecs_cluster.pipeline.id
  task_definition = aws_ecs_task_definition.pipeline.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets          = data.aws_subnets.c22-subnets.ids
    security_groups  = [aws_security_group.pipeline_task_sg.id]
    assign_public_ip = true
  }
}

# ECS task definition for the pipeline
resource "aws_ecs_task_definition" "pipeline" {
  family                   = "c22-jessh-etl-task"
  execution_role_arn       = aws_iam_role.ecs-setup-role.arn
  task_role_arn            = aws_iam_role.ecs-pipeline-role.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"

  container_definitions = jsonencode([{
    name  = "t3-pipeline"
    image = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c22-jessh-etl-ecr:latest"
    environment = [
      { name = "DB_HOST",            value = var.db_host },
      { name = "DB_PORT",            value = var.db_port },
      { name = "DB_NAME",            value = var.db_name },
      { name = "DB_USER",            value = var.db_user },
      { name = "DB_PASSWORD",        value = var.db_password },
      { name = "S3_DATASET_PATH",    value = "s3://c22-jessh-food-truck-bucket/" },
      { name = "AWS_DEFAULT_REGION", value = "eu-west-2" }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group        = "/ecs/c22-jessh-etl-ecr"
        awslogs-region       = "eu-west-2"
        awslogs-stream-prefix = "ecs"
      }
    }

  }])
}