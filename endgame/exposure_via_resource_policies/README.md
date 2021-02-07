# Resources that can be made public through resource policies

## Supported

### CloudWatch Logs
Actions:
- logs [put-resource-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/logs/put-resource-policy.html)

### ECR Repository
Actions:
- ecr [set-repository-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ecr/set-repository-policy.html)

### EFS
TODO: Need to confirm this can actually be shared with other accounts. Some of the doc wording leads me to think this might only be shareable to principals within an account.

Actions:
- efs [put-file-system-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/efs/put-file-system-policy.html)

### ElasticSearch
Actions:
- es [create-elasticsearch-domain](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/es/create-elasticsearch-domain.html)
- es [update-elasticsearch-domain-config](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/es/update-elasticsearch-domain-config.html)

### Glacier
Actions:
- glacier [set-vault-access-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/glacier/set-vault-access-policy.html)

### Lambda
Allows invoking the function

Actions:
- lambda [add-permission](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/lambda/add-permission.html)

### Lambda layer
Actions:
- lambda [add-layer-version-permission](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/lambda/add-layer-version-permission.html)

### IAM Role
Actions:
- iam [create-role](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/iam/create-role.html)
- iam [update-assume-role-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/iam/update-assume-role-policy.html)

### KMS Keys
Actions:
- kms [create-key](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/kms/create-key.html)
- kms [create-grant](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/kms/create-grant.html)
- kms [put-key-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/kms/put-key-policy.html)

### S3
S3 buckets can be public via policies and ACL. ACLs can be set at bucket or object creation.

Actions:
- s3api [create-bucket](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/s3api/create-bucket.html)
- s3api [put-bucket-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/s3api/put-bucket-policy.html)
- s3api [put-bucket-acl](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/s3api/put-bucket-acl.html)

### Secrets Managers
Actions:
- secretsmanager [put-resource-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/secretsmanager/put-resource-policy.html)



### SNS
Actions:
- sns [create-topic](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/sns/create-topic.html)
- sns [add-permission](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/sns/add-permission.html)

### SQS
Actions:
- sqs [create-queue](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/sqs/create-queue.html)
- sqs [add-permission](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/sqs/add-permission.html)


### SES
[Docs](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/sending-authorization-policies.html)

Actions:
- ses [put-identity-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ses/put-identity-policy.html)

## Not Supported

### Backup
[Docs](https://docs.aws.amazon.com/aws-backup/latest/devguide/creating-a-vault-access-policy.html)

Actions:
- backup [put-backup-vault-access-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/backup/put-backup-vault-access-policy.html)

### CloudWatch Logs (Destination Policies)

- logs [put-destination-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/logs/put-destination-policy.html)


### EventBridge
Only allows sending data into an account

Actions:
- events [put-permission](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/events/put-permission.html)

### Glue
Actions:
- glue [put-resource-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/glue/put-resource-policy.html)

### MediaStore
[Docs](https://docs.aws.amazon.com/mediastore/latest/ug/policies-examples-cross-acccount-full.html)

Actions:
- mediastore [put-container-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/mediastore/put-container-policy.html)

### Serverless Application Repository

Actions:
- serverlessrepo [put-application-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/serverlessrepo/put-application-policy.html)


### S3 Objects

S3 objects can be public via ACL. ACLs can be set at bucket or object creation.

- s3api [put-object](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/s3api/put-object.html)
- s3api [put-object-acl](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/s3api/put-object-acl.html)
