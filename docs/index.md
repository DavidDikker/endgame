# Endgame: Creating Backdoors in AWS

An AWS Pentesting tool that lets you use one-liner commands to backdoor an AWS account's resources with a rogue AWS account - or share the resources with the entire Internet 😈

<p align="center">
  <img src="images/endgame.gif">
</p>


Endgame abuses AWS's resource permission model to grant rogue users (or the Internet) access to an AWS account's resources with a single command. It does this through one of three methods:

1. Modifying [resource-based policies](https://endgame.readthedocs.io/en/latest/resource-policy-primer/) (such as [S3 Bucket policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteAccessPermissionsReqd.html#bucket-policy-static-site) or [Lambda Function policies](https://docs.aws.amazon.com/lambda/latest/dg/access-control-resource-based.html#permissions-resource-xaccountinvoke))
2. Resources that can be made public through sharing APIs (such as [Amazon Machine Images (AMIs)](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/sharingamis-explicit.html), [EBS disk snapshots](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ebs-modifying-snapshot-permissions.html), and [RDS database snapshots](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ShareSnapshot.html))
3. Sharing resources via [AWS Resource Access Manager (RAM)](https://docs.aws.amazon.com/ram/latest/userguide/shareable.html)

Endgame was created to:

* Push [AWS](https://endgame.readthedocs.io/en/latest/recommendations-to-aws/) to improve coverage of AWS Access Analyzer so AWS users can protect themselves.
* Show [blue teams](https://endgame.readthedocs.io/en/latest/recommendations-to-blue-teams/) and developers what kind of damage can be done by overprivileged/leaked accounts.
* Help red teams to demonstrate impact of their access.

Endgame demonstrates (with a bit of shock and awe) how simple human errors in excessive permissions (such a granting `s3:*` access instead of `s3:GetObject`) can be abused by attackers. These are not new attacks, but AWS's ability to **detect** _and_ **prevent** these attacks falls short of what customers need to protect themselves. This is what inspired us to write this tool. Follow the [Tutorial](./tutorial.md) and observe how you can expose resources across **17 different AWS services** to the Internet in a matter of seconds.

The resource types that can be exposed are of high value to attackers. This can include:

* Privileged compute access (by exposing who can invoke `lambda` functions)
* Database snapshots (`rds`), Storage buckets (`s3`), file systems (`elasticfilesystem`), storage backups (`glacier`), disk snapshots (`ebs` snapshots),
* Encryption keys (`kms`), secrets (`secretsmanager`), and private certificate authorities (`acm-pca`)
* Messaging and notification services (`sqs` queues, `sns` topics, `ses` authorized senders)
* Compute artifacts (`ec2` AMIs, `ecr` images, `lambda` layers)
* Logging endpoints (`cloudwatch` resource policies)
* Search and analytics engines (`elasticsearch` clusters)

Endgame is an attack tool, but it was written with a specific purpose. We wrote this tool with desired outcomes for the following audiences:

1. **AWS**: We want AWS to empower their customers with the capabilities to fight these attacks. Our recommendations are outlined in the [Recommendations to AWS](./recommendations-to-aws.md) section.
2. **AWS Customers and their customers**: It is better to have risks be more easily understood and know how to mitigate those risks than to force people to fight something novel. By increasing awareness about Resource Exposure and excessive permissions, we can protect ourselves against attacks where the attackers previously held the advantage and AWS customers were previously left blind.
3. **Blue Teams**: Defense teams can leverage the guidance around user-agent detection, API call detection, and behavioral detection outlined in the [Recommendations to Blue Teams](prevention.md) section.
4. **Red Teams**: This will make for some very eventful red team exercises. Make sure you give the Blue Team kudos when they catch you!


## Supported Backdoors

Endgame can create backdoors for resources in any of the services listed in the table below.

Note: At the time of this writing, [AWS Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html) does **NOT** support auditing **11 out of the 18 services** that Endgame attacks. Given that Access Analyzer is intended to detect this exact kind of violation, we kindly suggest to the AWS Team that they support all resources that can be attacked using Endgame. 😊

| Backdoor Resource Type                                  | Endgame | [AWS Access Analyzer Support][1] |
|---------------------------------------------------------|---------|----------------------------------|
| [ACM Private CAs](risks/acm-pca.md)                | ✅     | ❌                               |
| [CloudWatch Resource Policies](risks/logs.md)      | ✅     | ❌                               |
| [EBS Volume Snapshots](risks/ebs.md)               | ✅     | ❌                               |
| [EC2 AMIs](risks/amis.md)                          | ✅     | ❌                               |
| [ECR Container Repositories](risks/ecr.md)         | ✅     | ❌                               |
| [EFS File Systems](risks/efs.md)                   | ✅     | ❌                               |
| [ElasticSearch Domains](risks/es.md)               | ✅     | ❌                               |
| [Glacier Vault Access Policies](risks/glacier.md)  | ✅     | ❌                               |
| [IAM Roles](risks/iam-roles.md)                    | ✅     | ✅                               |
| [KMS Keys](risks/kms.md)                           | ✅     | ✅                               |
| [Lambda Functions](risks/lambda-functions.md)      | ✅     | ✅                               |
| [Lambda Layers](risks/lambda-layers.md)            | ✅     | ✅                               |
| [RDS Snapshots](risks/rds-snapshots.md)            | ✅     | ❌                               |
| [S3 Buckets](risks/s3.md)                          | ✅     | ✅                               |
| [Secrets Manager Secrets](risks/secretsmanager.md) | ✅     | ✅                               |
| [SES Sender Authorization Policies](risks/ses.md)  | ✅     | ❌                               |
| [SQS Queues](risks/sqs.md)                         | ✅     | ✅                               |
| [SNS Topics](risks/sns.md)                         | ✅     | ❌                               |

[1]: https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html
