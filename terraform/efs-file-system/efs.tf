resource "aws_efs_file_system" "foo" {
  creation_token = var.name

  tags = {
    Name = var.name
  }
}