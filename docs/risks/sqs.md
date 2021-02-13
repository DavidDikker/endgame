# SQS

## Steps to Reproduce

## Example

## Exploitation

## Remediation

* **Trusted Accounts Only**: Ensure that SQS Queues are only shared with trusted accounts, and that the trusted accounts truly need access to the SQS Queue.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **AWS Access Analyzer**: Leverage AWS Access Analyzer to report on external access to  SQS Queues. See [the AWS Access Analyzer documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html) for more details.
* **Restrict access to IAM permissions that could lead to exposure of your SQS Queues**: Tightly control access to the following IAM actions:
  - [sqs:AddPermission](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_AddPermission.html): _Description_
  - [sqs:RemovePermission](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_RemovePermission.html): _Description_
  - [sqs:GetQueueAttributes](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_GetQueueAttributes.html): _Gets attributes for the specified queue. This includes retrieving the list of principals who are authorized to access the queue._
  - [sqs:GetQueueUrl](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_GetQueueUrl.html): _Returns the URL of an existing queue._
  - [sqs:ListQueues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_ListQueues.html): _Returns a list of your queues._

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## References

* [add-permission](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/sqs/add-permission.html)