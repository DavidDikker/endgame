# IAM Roles (via AssumeRole)

## Steps to Reproduce

## Example

## Exploitation

## Remediation

* **Trusted Accounts Only**: Ensure that IAM roles can only be assumed by trusted accounts and the trusted principals within those accounts.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **AWS Access Analyzer**: Leverage AWS Access Analyzer to report on external access to Assume IAM Roles. See [the AWS Access Analyzer documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html) for more details.
* **Restrict access to IAM permissions that could lead to exposure of your IAM Roles**: Tightly control access to the following IAM actions:
  - [iam:UpdateAssumeRolePolicy](https://docs.aws.amazon.com/IAM/latest/APIReference/API_UpdateAssumeRolePolicy.html): _Grants permission to update the policy that grants an IAM entity permission to assume a role_
  - [iam:GetRole](https://docs.aws.amazon.com/IAM/latest/APIReference/API_GetRole.html): _Grants permission to retrieve information about the specified role, including the role's path, GUID, ARN, and the role's trust policy_
  - [iam:ListRoles](https://docs.aws.amazon.com/IAM/latest/APIReference/API_ListRoles.html): _Grants permission to list the IAM roles that have the specified path prefix_

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## References

* [update-assume-role-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/iam/update-assume-role-policy.html)