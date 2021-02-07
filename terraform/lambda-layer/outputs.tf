output "arn" {
  value = aws_lambda_layer_version.lambda_layer.layer_arn
}

output "name" {
  value = "${var.name}:${aws_lambda_layer_version.lambda_layer.version}"
}