variable "db_host" {}
variable "db_port" {}
variable "db_name" {}
variable "db_user" {}
variable "db_password" {}
variable "vpc_id" {}
variable "subnet_ids" {
  type = list(string)
}