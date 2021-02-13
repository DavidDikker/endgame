# Elastic File Systems (EFS)

## Steps to Reproduce

## Example

## Exploitation

## Remediation

> ‼️ **Note**: At the time of this writing, AWS Access Analyzer does **NOT** support auditing of this resource type to prevent resource exposure. **We kindly suggest to the AWS Team that they support all resources that can be attacked using this tool**. 😊

* **Trusted Accounts Only**: Ensure that EFS File Systems are only shared with trusted accounts, and that the trusted accounts truly need access to the File System.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **Restrict access to IAM permissions that could lead to exposure of your EFS File Systems**: Tightly control access to the following IAM actions:
  - [elasticfilesystem:PutFileSystemPolicy](https://docs.aws.amazon.com/efs/latest/ug/API_PutFileSystemPolicy.html): _Grants permission to apply a resource-level policy that defines the actions allowed or denied from given actors for the specified file system_
  - [elasticfilesystem:DescribeFileSystems](https://docs.aws.amazon.com/efs/latest/ug/API_DescribeFileSystems.html): _Grants permission to view the description of an Amazon EFS file system specified by file system CreationToken or FileSystemId; or to view the description of all file systems owned by the caller's AWS account in the AWS region of the endpoint that is being called_
  - [elasticfilesystem:DescribeFileSystemPolicy](https://docs.aws.amazon.com/efs/latest/ug/API_DescribeFileSystemPolicy.html): _Grants permission to view the resource-level policy for an Amazon EFS file system_

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## References

* [put-filesystem-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/efs/put-file-system-policy.html)