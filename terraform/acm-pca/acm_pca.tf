# https://docs.aws.amazon.com/acm-pca/latest/userguide/pca-rbp.html

resource "aws_acmpca_certificate_authority" "example" {
  certificate_authority_configuration {
    key_algorithm     = "RSA_4096"
    signing_algorithm = "SHA512WITHRSA"

    subject {
      organization = var.name
      common_name = var.name
    }
  }

  permanent_deletion_time_in_days = 7
  type = "ROOT"
}