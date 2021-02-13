import copy
SUPPORTED_AWS_SERVICES = [
  "all",
  "acm-pca",
  "ec2-ami",
  "ebs",
  "ecr",
  "efs",
  "elasticsearch",
  "glacier",
  "iam",
  "kms",
  "lambda",
  "lambda-layer",
  "cloudwatch",
  "rds",
  "s3",
  "secretsmanager",
  "ses",
  "sns",
  "sqs",
]
EMPTY_POLICY = {"Version": "2012-10-17", "Statement": []}
EC2_ASSUME_ROLE_POLICY = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
LAMBDA_ASSUME_ROLE_POLICY = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

# THIS VARIABLE IS KEY. Let's say you are doing a blue team test, and you are trying to see if your team picked up on
#   any modifications that were made using this tool. You can loop through policies that have this SID value to see how
#   accurate your detection mechanisms were at picking up vulnerable resource-based policies like this.
# Any IAM Policy with a statement added from this tool will include the value of this variable.
SID_SIGNATURE = "Endgame"
ALLOW_CURRENT_ACCOUNT_SID_SIGNATURE = "AllowCurrentAccount"
# This can be used by blue team to identify API calls in CloudTrail executed by this tool.
USER_AGENT_INDICATOR = "HotDogsAreSandwiches"


def get_empty_policy():
    """Return a copy of an empty policy"""
    return copy.deepcopy(EMPTY_POLICY)
