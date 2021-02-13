# KMS Keys

## Steps to Reproduce

## Example

## Exploitation

## Remediation
* **Trusted Accounts Only**: Ensure that KMS Keys are only shared with trusted accounts, and that the trusted accounts truly need access to the key.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **AWS Access Analyzer**: Leverage AWS Access Analyzer to report on external access to  KMS Keys. See [the AWS Access Analyzer documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html) for more details.
* **Restrict access to IAM permissions that could lead to exposure of your KMS Keys**: Tightly control access to the following IAM actions:
  - [kms:PutKeyPolicy](https://docs.aws.amazon.com/kms/latest/APIReference/API_PutKeyPolicy.html): _Controls permission to replace the key policy for the specified customer master key_
  - [kms:GetKeyPolicy](https://docs.aws.amazon.com/kms/latest/APIReference/API_GetKeyPolicy.html): _Controls permission to view the key policy for the specified customer master key_
  - [kms:ListKeys](https://docs.aws.amazon.com/kms/latest/APIReference/API_ListKeys.html): _Controls permission to view the key ID and Amazon Resource Name (ARN) of all customer master keys in the account_
  - [kms:ListAliases](https://docs.aws.amazon.com/kms/latest/APIReference/API_ListAliases.html): _Controls permission to view the aliases that are defined in the account. Aliases are optional friendly names that you can associate with customer master keys_

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## References

* [put-key-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/kms/put-key-policy.html)