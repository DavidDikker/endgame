module "acm_pca" {
  source = "./acm-pca"
}

module "cloudwatch_resource_policy" {
  source = "./cloudwatch-resource-policy"
}

module "ecr" {
  source = "./ecr-repository"
}

module "efs" {
  source = "./efs-file-system"
}

//module "elasticsearch_domain" {
//  source = "./elasticsearch-domain"
//}

module "glacier" {
  source = "./glacier-vault"
}

//module "iam_role" {
//  source = "./iam-role"
//}

//module "lambda_function" {
//  source = "./lambda-function"
//}

//module "lambda_layer" {
//  source = "./lambda-layer"
//}

//module "s3_bucket" {
//  source = "./s3-bucket"
//}

module "secrets_manager" {
  source = "./secrets-manager"
}

module "ses_identity" {
  source      = "./ses-domain-identity"
}

//module "sns_topic" {
//  source = "./sns-topic"
//}

module "sqs_queue" {
  source = "./sqs-queue"
}

/*
ElasticSearch Domain: ${module.elasticsearch_domain.name}
IAM Role: ${module.iam_role.name}
Lambda Function: ${module.lambda_function.name}
Lambda Layer: ${module.lambda_layer.name}
S3 Bucket: ${module.s3_bucket.name}
SNS Topic: ${module.sns_topic.name}
*/

output "names" {
  value = <<README
ACM Private Certificate Authority (ACM PCA): ${module.acm_pca.arn}
SES Identity: ${module.ses_identity.name}
ECR Registry: ${module.ecr.name}
EFS File System: ${module.efs.id}
Secrets Manager: ${module.secrets_manager.name}
SQS Queue: ${module.sqs_queue.name}
README
}

// For the ACM Private Certificate Authority, you will need to access the AWS console after it is created. See the tutorial for more instructions.
