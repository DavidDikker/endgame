# SNS

## Steps to Reproduce

* Using `endgame`:

* Using AWS CLI:

## Example: Exposed Resource

```json
{
  "Version": "2008-10-17",
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Sid": "Endgame",
      "Effect": "Allow",
      "Principal": {
        "AWS": "999988887777"
      },
      "Action": [
        "SNS:AddPermission",
        "SNS:DeleteTopic",
        "SNS:GetTopicAttributes",
        "SNS:ListSubscriptionsByTopic",
        "SNS:Publish",
        "SNS:Receive",
        "SNS:RemovePermission",
        "SNS:SetTopicAttributes",
        "SNS:Subscribe"
      ],
      "Resource": "arn:aws:sns:us-east-1:111122223333:test-resource-exposure"
    }
  ]
}
```

## Remediation

## References

* [add-permission](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/sns/add-permission.html)