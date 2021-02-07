resource "aws_lambda_function" "lambda_function" {
  role             = aws_iam_role.lambda_exec_role.arn
  handler          = "lambda.handler"
  runtime          = "python3.8"
  filename         = abspath("${path.module}/lambda.zip")
  function_name    = var.name
  source_code_hash = filesha256(abspath("${path.module}/lambda.zip"))
}

resource "aws_iam_role" "lambda_exec_role" {
  name        = "${var.name}-lambda"
  path        = "/"
  description = "Allows Lambda Function to call AWS services on your behalf."

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}
