# IAM Permissions

The IAM Permissions listed below are used to create these backdoors.

You don't need **all** of these permissions to run the tool. You just need enough from each service. For example, `s3:ListAllMyBuckets`, `s3:GetBucketPolicy`, and `s3:PutBucketPolicy` are all the permissions needed to leverage this tool to expose S3 buckets.

```json
{
    "Version": "2012-10-17",
    "Statement": [
            {
            "Sid": "IAmInevitable",
            "Effect": "Allow",
            "Action": [
                "acm-pca:DeletePolicy",
                "acm-pca:GetPolicy",
                "acm-pca:ListCertificateAuthorities",
                "acm-pca:PutPolicy",
                "ec2:DescribeImageAttribute",
                "ec2:DescribeImages",
                "ec2:DescribeSnapshotAttribute",
                "ec2:DescribeSnapshots",
                "ec2:ModifySnapshotAttribute",
                "ec2:ModifyImageAttribute",
                "ecr:DescribeRepositories",
                "ecr:DeleteRepositoryPolicy",
                "ecr:GetRepositoryPolicy",
                "ecr:SetRepositoryPolicy",
                "elasticfilesystem:DescribeFileSystems",
                "elasticfilesystem:DescribeFileSystemPolicy",
                "elasticfilesystem:PutFileSystemPolicy",
                "es:DescribeElasticsearchDomainConfig",
                "es:ListDomainNames",
                "es:UpdateElasticsearchDomainConfig",
                "glacier:GetVaultAccessPolicy",
                "glacier:ListVaults",
                "glacier:SetVaultAccessPolicy",
                "iam:GetRole",
                "iam:ListRoles",
                "iam:UpdateAssumeRolePolicy",
                "kms:GetKeyPolicy",
                "kms:ListKeys",
                "kms:ListAliases",
                "kms:PutKeyPolicy",
                "lambda:AddLayerVersionPermission",
                "lambda:AddPermission",
                "lambda:GetPolicy",
                "lambda:GetLayerVersionPolicy",
                "lambda:ListFunctions",
                "lambda:ListLayers",
                "lambda:ListLayerVersions",
                "lambda:RemoveLayerVersionPermission",
                "lambda:RemovePermission",
                "logs:DescribeResourcePolicies",
                "logs:DeleteResourcePolicy",
                "logs:PutResourcePolicy",
                "rds:DescribeDbClusterSnapshots",
                "rds:DescribeDbClusterSnapshotAttributes",
                "rds:DescribeDbSnapshots",
                "rds:DescribeDbSnapshotAttributes",
                "rds:ModifyDbSnapshotAttribute",
                "rds:ModifyDbClusterSnapshotAttribute",
                "s3:GetBucketPolicy",
                "s3:ListAllMyBuckets",
                "s3:PutBucketPolicy",
                "secretsmanager:GetResourcePolicy",
                "secretsmanager:DeleteResourcePolicy",
                "secretsmanager:ListSecrets",
                "secretsmanager:PutResourcePolicy",
                "ses:DeleteIdentityPolicy",
                "ses:GetIdentityPolicies",
                "ses:ListIdentities",
                "ses:ListIdentityPolicies",
                "ses:PutIdentityPolicy",
                "sns:AddPermission",
                "sns:ListTopics",
                "sns:GetTopicAttributes",
                "sns:RemovePermission",
                "sqs:AddPermission",
                "sqs:GetQueueUrl",
                "sqs:GetQueueAttributes",
                "sqs:ListQueues",
                "sqs:RemovePermission"
            ],
            "Resource": "*"
        }
    ]
}
```

