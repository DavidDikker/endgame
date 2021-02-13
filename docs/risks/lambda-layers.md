# Lambda Layers

## Steps to Reproduce

## Example

## Exploitation

## Remediation

* **Trusted Accounts Only**: Ensure that Lambda Layers are only shared with trusted accounts.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **AWS Access Analyzer**: Leverage AWS Access Analyzer to report on external access to Lambda Layers. See [the AWS Access Analyzer documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html#access-analyzer-lambda) for more details.
* **Restrict access to IAM permissions that could expose your Lambda Layers**: Tightly control access to the following IAM actions:
  - [lambda:AddLayerVersionPermission](https://docs.aws.amazon.com/lambda/latest/dg/API_AddLayerVersionPermission.html): _Grants permission to add permissions to the resource-based policy of a version of an AWS Lambda layer_
  - [lambda:GetLayerVersionPolicy](https://docs.aws.amazon.com/lambda/latest/dg/API_GetLayerVersionPolicy.html): _Grants permission to view the resource-based policy for a version of an AWS Lambda layer_
  - [lambda:ListFunctions](https://docs.aws.amazon.com/lambda/latest/dg/API_ListFunctions.html): _Grants permission to retrieve a list of AWS Lambda functions, with the version-specific configuration of each function_
  - [lambda:ListLayers](https://docs.aws.amazon.com/lambda/latest/dg/API_ListLayers.html): _Grants permission to retrieve a list of AWS Lambda layers, with details about the latest version of each layer_
  - [lambda:ListLayerVersions](https://docs.aws.amazon.com/lambda/latest/dg/API_ListLayerVersions.html): _Grants permission to retrieve a list of versions of an AWS Lambda layer_
  - [lambda:RemoveLayerVersionPermission](https://docs.aws.amazon.com/lambda/latest/dg/API_RemoveLayerVersionPermission.html): _Grants permission to remove a statement from the permissions policy for a version of an AWS Lambda layer_

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## References

* [aws lambda add-layer-version-permission](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/lambda/add-layer-version-permission.html)
* [Access Analyzer support for AWS Lambda Functions](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html#access-analyzer-lambda)
