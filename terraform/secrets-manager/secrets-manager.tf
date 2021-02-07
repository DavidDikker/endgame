resource "aws_secretsmanager_secret" "test_resource_exposure" {
  name = var.name
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "example" {
  secret_id     = aws_secretsmanager_secret.test_resource_exposure.id
  secret_string = "foosecret"
}