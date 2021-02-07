output "arn" {
  value = aws_secretsmanager_secret.test_resource_exposure.arn
}

output "name" {
  value = aws_secretsmanager_secret.test_resource_exposure.name
}