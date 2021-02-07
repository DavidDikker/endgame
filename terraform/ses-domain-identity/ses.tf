resource "aws_ses_domain_identity" "example" {
  domain = var.domain_name
}
//
//resource "aws_route53_record" "example_amazonses_verification_record" {
//  zone_id = data.aws_route53_zone.selected.zone_id
//  name    = "_amazonses.example.com"
//  type    = "TXT"
//  ttl     = "600"
//  records = [aws_ses_domain_identity.example.verification_token]
//}
//
//data "aws_route53_zone" "selected" {
//  name         = "${var.domain_name}."
//  private_zone = false
//}