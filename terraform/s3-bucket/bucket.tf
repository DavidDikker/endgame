resource "aws_s3_bucket" "test_resource_exposure" {
  bucket = "${var.name_prefix}-${random_string.random.result}"
}

resource "aws_s3_bucket_object" "test_object" {
  bucket = aws_s3_bucket.test_resource_exposure.bucket
  key = "kinnaird-was-here.txt"
}

resource "random_string" "random" {
  length = 16
  special = false
  min_lower = 16
}