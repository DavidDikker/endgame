# Prevention

There are 6 general methods that blue teams can use to **prevent** AWS Resource Exposure Attacks:

1. Use AWS KMS Customer-Managed Keys to encrypt resources
2. Leverage Strong Resource-based Policies
3. Trusted Accounts Only
4. Inventory which IAM Principals are capable of Resource Exposure
5. AWS Service Control Policies
6. Prevent AWS RAM External Principals

## Use AWS KMS Customer-Managed Keys

If an attacker does not have access to your Customer Managed Key, the attacker cannot access the resource. You can leverage this strategy to prevent cases in which your resources are leaked to the internet but the attacker did not have access to the encryption key.

Additionally, use strong resource-based policies on the Customer Managed Keys and leverage them to prevent other IAM Principals in the account from using that key for decrypt operations or management operations. If the attacker cannot use the key to decrypt, they effectively cannot access the resource.

## Leverage strong resource-based policies

Strong resource-based policies can ensure that only the intended IAM principals can modify the KMS key policy (i.e, using `kms:PutKeyPolicy` permissions. Under this scenario, even if an attacker has privileged access, if they are not granted `kms:PutKeyPolicy` by the KMS key, then they can't subvert your KMS encryption.

## Trusted Accounts Only

Practice good security hygiene throughout your SDLC. Ensure that only trusted accounts are allowed any level of access to your accounts, especially via resource-based policies.

## Inventory which IAM Principals are Capable of Resource Exposure

Consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## AWS Service Control Policies (SCPs)

AWS Service Control Policies (SCPs) cannot be used to strictly prevent resources from becoming public.

However, there are well-known AWS Service Control Policies that can force encryption on EBS and RDS snapshots, which essentially also blocks public access as mentioned above.

### Enforce RDS Encryption

As covered in [this blog post](https://medium.com/@cbchhaya/aws-scp-to-mandate-rds-encryption-6b4dc8b036a), the following AWS SCP can be used to Mandate RDS Encryption:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "StatementForOtherRDS",
            "Effect": "Deny",
            "Action": [
                "rds:CreateDBInstance"
            ],
            "Resource": [
                "*"
            ],
            "Condition": {
                "ForAnyValue:StringEquals": {
                    "rds:DatabaseEngine": [
                        "mariadb",
                        "mysql",
                        "oracle-ee",
                        "oracle-se2",
                        "oracle-se1",
                        "oracle-se",
                        "postgres",
                        "sqlserver-ee",
                        "sqlserver-se",
                        "sqlserver-ex",
                        "sqlserver-web"
                    ]
                },
                "Bool": {
                    "rds:StorageEncrypted": "false"
                }
            }
        },
        {
            "Sid": "StatementForAurora",
            "Effect": "Deny",
            "Action": [
                "rds:CreateDBCluster"
            ],
            "Resource": [
                "*"
            ],
            "Condition": {
                "Bool": {
                    "rds:StorageEncrypted": "false"
                }
            }
        }
    ]
}
```

### Require Encryption on All S3 Buckets

The following SCP requires that all Amazon S3 buckets use AES256 encryption in an AWS Account.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "s3:PutObject"
            ],
            "Resource": "*",
            "Effect": "Deny",
            "Condition": {
                "StringNotEquals": {
                    "s3:x-amz-server-side-encryption": "AES256"
                }
            }
        },
        {
            "Action": [
                "s3:PutObject"
            ],
            "Resource": "*",
            "Effect": "Deny",
            "Condition": {
                "Bool": {
                    "s3:x-amz-server-side-encryption": false
                }
            }
        }
    ]
}
```

### Protect S3 Block Public Access

After setting up your AWS account, set the [S3 Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html) to enforce at the AWS Account level (not just the bucket level). Then, apply this SCP to prevent users or roles in any affected account from modifying the S3 Block Public Access Settings in an Account.

Note: This will only eliminate the risk of modifying an S3 bucket policy to allow `*` Principals. It will not eliminate the risk of modifying an S3 bucket policy to allow rogue IAM users or rogue accounts.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "s3:PutBucketPublicAccessBlock"
      ],
      "Resource": "*",
      "Effect": "Deny"
    }
  ]
}
```

### Protect AWS Access Analyzer

While AWS Access Analyzer has its shortcomings, it is a uniquely useful tool that you should use to help address the risk of Resource Exposure Attacks.

When using AWS Access Analyzer, it is paramount that AWS Access Analyzer configuration is protected against malicious modification by users who seek to disable security alerts before performing malicious activities.

The following SCP prevents users or roles in any affected account from deleting AWS Access Analyzer in an AWS account:

```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "access-analyzer:DeleteAnalyzer"
      ],
      "Resource": "*",
      "Effect": "Deny"
    }
  ]
}
```


### Prevent AWS RAM External Principals

This SCP prevents users or roles in any affected account from creating Resource Access Shares using RAM that are shared with external principals outside the organization. This can categorically eliminate one of the three methods of Resource Exposure identified by Endgame and is highly suggested.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "*"
      ],
      "Resource": "*",
      "Effect": "Deny",
      "Condition": {
        "Bool": {
          "ram:AllowsExternalPrincipals": "true"
        }
      }
    }
  ]
}
```


## Further Reading

* [Blog Post about Using AWS SCPs to Mandate RDS Encryption](https://medium.com/@cbchhaya/aws-scp-to-mandate-rds-encryption-6b4dc8b036a)