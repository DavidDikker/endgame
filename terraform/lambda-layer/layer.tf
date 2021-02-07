data "archive_file" "layer" {
  source_dir = "${path.module}/python/"
  output_path = "${path.module}/python_libs.zip"
  type        = "zip"
}

resource "aws_lambda_layer_version" "lambda_layer" {
  filename            = data.archive_file.layer.output_path
  layer_name          = var.name
  source_code_hash    = data.archive_file.layer.output_base64sha256
  compatible_runtimes = ["python3.7"]
}

resource "aws_lambda_layer_version" "lambda_layer_2" {
  filename            = data.archive_file.layer.output_path
  layer_name          = "${var.name}-a"
  source_code_hash    = data.archive_file.layer.output_base64sha256
  compatible_runtimes = ["python3.7"]
}