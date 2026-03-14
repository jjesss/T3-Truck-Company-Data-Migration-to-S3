# ECR, ECS

provider "aws" {
  region = "eu-west-2"
}

# ECR Repository
resource "aws_ecr_repository" "dashboard" {
  name = "c22-jessh-t3-dashboard"
}

# ECS Cluster
resource "aws_ecs_cluster" "dashboard" {
  name = "c22-jessh-t3-dashboard-cluster"
}

# IAM Role for ECS Task
resource "aws_iam_role" "ecs_task_role" {
  name = "c22-jessh-t3-ecs-task-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}
resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
resource "aws_iam_role" "ecs_execution_role" {
  name = "c22-jessh-t3-ecs-execution-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}
resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ECS Task Definition
resource "aws_ecs_task_definition" "dashboard" {
  family                   = "c22-jessh-t3-dashboard"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn

  container_definitions = jsonencode([{
    name  = "dashboard"
    image = "${aws_ecr_repository.dashboard.repository_url}:latest"
    portMappings = [{
      containerPort = 8501
      hostPort      = 8501
    }]
    environment = [
      { name = "AWS_ACCESS_KEY_ID",     value = var.aws_access_key_id },
      { name = "AWS_SECRET_ACCESS_KEY", value = var.aws_secret_access_key },
      { name = "AWS_DEFAULT_REGION",    value = "eu-west-2" }
    ]
  }])
}

# Secuirity Group
resource "aws_security_group" "dashboard" {
  name   = "c22-jessh-t3-dashboard-sg"
  vpc_id = var.vpc_id

  ingress {
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ECS Service
resource "aws_ecs_service" "dashboard" {
  name            = "c22-jessh-t3-dashboard-service"
  cluster         = aws_ecs_cluster.dashboard.id
  task_definition = aws_ecs_task_definition.dashboard.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [aws_security_group.dashboard.id]
    assign_public_ip = true
  }
}