# Elastic Container Registries (ECR)

## Steps to Reproduce

## Example

## Exploitation

## Remediation

> ‼️ **Note**: At the time of this writing, AWS Access Analyzer does **NOT** support auditing of this resource type to prevent resource exposure. **We kindly suggest to the AWS Team that they support all resources that can be attacked using this tool**. 😊

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

## References

* [set-repository-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ecr/set-repository-policy.html)