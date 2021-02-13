# Glacier Vault

## Steps to Reproduce

## Example

## Exploitation

## Remediation

> ‼️ **Note**: At the time of this writing, AWS Access Analyzer does **NOT** support auditing of this resource type to prevent resource exposure. **We kindly suggest to the AWS Team that they support all resources that can be attacked using this tool**. 😊

* **Trusted Accounts Only**: Ensure that Glacier Vaults are only shared with trusted accounts, and that the trusted accounts truly need access to the Vaults.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **Restrict access to IAM permissions that could lead to exposure of your Vaults**: Tightly control access to the following IAM actions:
  - [glacier:GetVaultAccessPolicy](https://docs.aws.amazon.com/amazonglacier/latest/dev/api-GetVaultAccessPolicy.html): _Retrieves the access-policy subresource set on the vault_
  - [glacier:ListVaults](https://docs.aws.amazon.com/amazonglacier/latest/dev/api-vaults-get.html): _Lists all vaults_
  - [glacier:SetVaultAccessPolicy](https://docs.aws.amazon.com/amazonglacier/latest/dev/api-SetVaultAccessPolicy.html): _Configures an access policy for a vault and will overwrite an existing policy._

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## References

* [set-vault-access-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/glacier/set-vault-access-policy.html)