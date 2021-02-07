resource "aws_elasticsearch_domain" "example" {
  domain_name           = var.name
  elasticsearch_version = "1.5"

  cluster_config {
    instance_type = "t2.micro.elasticsearch"
    instance_count = 1
  }
  ebs_options {
    ebs_enabled = true
    volume_size = 20

  }

  tags = {
    Domain = var.name
  }
}