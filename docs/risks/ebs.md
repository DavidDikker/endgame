# EBS Snapshot Exposure

## Steps to Reproduce

## Example

## Exploitation

## Remediation

> ‼️ **Note**: At the time of this writing, AWS Access Analyzer does **NOT** support auditing of this resource type to prevent resource exposure. **We kindly suggest to the AWS Team that they support all resources that can be attacked using this tool**. 😊

* **Trusted Accounts Only**: Ensure that EBS Snapshots are only shared with trusted accounts, and that the trusted accounts truly need access to the EBS Snapshot.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **Restrict access to IAM permissions that could lead to exposure of your EBS Snapshots**: Tightly control access to the following IAM actions:
  - [ec2:ModifySnapshotAttribute](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_ModifySnapshotAttribute.html): _Grants permission to add or remove permission settings for a snapshot_
  - [ec2:DescribeSnapshotAttribute](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeSnapshotAttribute.html): _Grants permission to describe an attribute of a snapshot. This includes information on which accounts the snapshot has been shared with._
  - [ec2:DescribeSnapshots](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeSnapshots.html): _Grants permission to describe one or more EBS snapshots_

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## References

* [Sharing an Unencrypted Snapshot using the Console](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-modifying-snapshot-permissions.html#share-unencrypted-snapshot)
* [Share a snapshot using the command line](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-modifying-snapshot-permissions.html)
