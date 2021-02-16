# ElasticSearch Domains

* [Steps to Reproduce](#steps-to-reproduce)
* [Exploitation](#exploitation)
* [Remediation](#remediation)
* [Basic Detection](#basic-detection)
* [References](#references)

> Note: The **Network Configuration** settings in ElasticSearch clusters offer two options - **VPC Access** or **Public access**. If VPC access is used, modification of the resource-based policy - whether using `endgame` or the CLI exploitation method - will not result in access to the internet. `endgame` only modifies the resource-based policy for the ElasticSearch cluster, so this will only expose ElasticSearch clusters that are set to **Public access*.

## Steps to Reproduce

* To expose the resource using `endgame`, run the following from the victim account:

```bash
export EVIL_PRINCIPAL=arn:aws:iam::999988887777:user/evil

endgame expose --service elasticsearch --name test-resource-exposure
```

* To get the content of the resource-based policy for ElasticSearch domain config, run the following command from the victim account:

```bash
aws es describe-elasticsearch-domain-config --domain-name test-resource-exposure
```

## Example

The response will contain a field titled `AccessPolicies`. AccessPolicies will contain content that resembles the below. Observe that the victim resource (`arn:aws:es:us-east-1:999988887777:domain/test-resource-exposure`) allows access to `*` principals, indicating a successful compromise.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "es:*",
      "Resource": "arn:aws:es:us-east-1:999988887777:domain/test-resource-exposure/*"
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

The **Network Configuration** settings in ElasticSearch clusters offer two options - **VPC Access** or **Public access**. If VPC access is used, modification of the resource-based policy - whether using `endgame` or the CLI exploitation method - will not result in access to the internet. `endgame` only modifies the resource-based policy for the ElasticSearch cluster, so this will only expose ElasticSearch clusters that are set to **Public access*.

* Consider Migrating from Public Access to VPC Access, if possible. This will help you avoid a situation where an attacker could expose your ElasticSearch cluster to the internet with a single API call. For more information, see the documentation on [Migrating from Public Access to VPC Access](https://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/es-vpc.html#es-migrating-public-to-vpc).

However, if **Public Access** _is_ necessary, follow the steps below to remediate this risk and reduce the likelihood that a compromise in your AWS account could lead to exposure of your ElasticSearch cluster.

* **Trusted Accounts Only**: Ensure that ElasticSearch Clusters are only shared with trusted accounts, and that the trusted accounts truly need access to the ElasticSearch cluster.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **Restrict access to IAM permissions that could lead to exposure of your ElasticSearch Clusters**: Tightly control access to the following IAM actions:
      - [es:UpdateElasticsearchDomainConfig](https://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/es-configuration-api.html#es-configuration-api-actions-updateelasticsearchdomainconfig): _Grants permission to modify the configuration of an Amazon ES domain, which includes the Resource-Based Policy (RBP) content. The RBP can be modified to allow access from external IAM principals or from the internet._
      - [es:DescribeElasticsearchDomainConfig](): _Grants permission to view a description of the configuration options and status of an Amazon ES domain. This includes the Resource Based Policy content, which contains information on which IAM principals are authorized to acccess the cluster._
      - [es:ListDomainNames](https://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/es-configuration-api.html#es-configuration-api-actions-listdomainnames): _Grants permission to display the names of all Amazon ES domains that the current user owns._

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## Basic Detection
The following CloudWatch Log Insights query will include exposure actions taken by endgame:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent
| filter eventSource='es.amazonaws.com' and eventName='UpdateElasticsearchDomainConfig'
```

This query assumes that your CloudTrail logs are being sent to CloudWatch and that you have selected the correct log group.

## References

* [ElasticSearch Resource-based Policies](https://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/es-ac.html#es-ac-types-resource)
* [Migrating from Public Access to VPC Access](https://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/es-vpc.html#es-migrating-public-to-vpc)
