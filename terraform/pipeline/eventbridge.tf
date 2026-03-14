# EventBridge Scheduler IAM Role
resource "aws_iam_role" "eventbridge-scheduler-role" {
  name = "c22-jessh-eventbridge-scheduler-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "scheduler.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "eventbridge-scheduler-policy" {
  name = "c22-jessh-eventbridge-scheduler-policy"
  role = aws_iam_role.eventbridge-scheduler-role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["ecs:RunTask", "iam:PassRole"]
        Resource = "*"
      }
    ]
  })
}

# EventBridge Schedule
resource "aws_scheduler_schedule" "etl-pipeline-schedule" {
  name = "c22-jessh-etl-schedule"

  schedule_expression = "cron(0 */3 * * ? *)"
  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = "arn:aws:ecs:eu-west-2:129033205317:cluster/c22-jessh-etl-cluster"
    role_arn = aws_iam_role.eventbridge-scheduler-role.arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.pipeline.arn
      launch_type         = "FARGATE"

      network_configuration {
        assign_public_ip = true  # ← this must be true
        subnets          = var.subnet_ids
        security_groups  = [aws_security_group.pipeline_task_sg.id]
        }
    }
  }
}