variable "vpc_id" {}
variable "subnet_ids" {
  type = list(string)
}
variable aws_access_key_id {}
variable aws_secret_access_key {}