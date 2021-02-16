# Recommendations to AWS

While [Cloudsplaining](https://opensource.salesforce.com/cloudsplaining/) (a Salesforce-produced AWS IAM assessment tool), showed us the pervasiveness of least privilege violations in AWS IAM across the industry, Endgame shows us how it is already easy for attackers. These are not new attacks, but AWS's ability to **detect** _and_ **prevent** these attacks falls short of what customers need to protect themselves.

[AWS Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html) is a tool produced by AWS that helps you identify the resources in your organization and accounts, such as Amazon S3 buckets or IAM roles, that are shared with an external entity. In short, it **detects** instances of this resource exposure problem. However, it does not by itself meet customer need, due to current gaps in coverage and the lack of preventative tooling to compliment it.

At the time of this writing, [AWS Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html) does **NOT** support auditing **11 out of the 18 services** that Endgame attacks. Given that Access Analyzer is intended to detect this exact kind of violation, we kindly suggest to the AWS Team that they support all resources that can be attacked using Endgame. 😊

The lack of preventative tooling makes this issue more difficult for customers. Ideally, customers should be able to say, _"Nobody in my AWS Organization is allowed to share **any** resources that can be exposed by Endgame outside of the organization, unless that resource is in an exemption list."_ This **should** be possible, but it is not. It is not even possible to use [AWS Service Control Policies (SCPS)](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html) - AWS's preventative guardrails service - to prevent `sts:AssumeRole` calls from outside your AWS Organization. The current SCP service limit of 5 SCPs per AWS account compounds this problem.

We recommend that AWS take the following measures in response:

* Increase Access Analyzer Support to cover the resources that can be exposed via Resource-based Policy modification, AWS RAM resource sharing, and resource-specific sharing APIs (such as RDS snapshots, EBS snapshots, and EC2 AMIs)
* Create GuardDuty rules that detect anomalous exposure of resources outside your AWS Organization.
* Expand the current limit of 5 SCPs per AWS account to 200. (for comparison, the Azure equivalent - Azure Policies - has a limit of [200 Policy or Initiative Assignments per subscription](https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/azure-subscription-service-limits#azure-policy-limits))
* Improve the AWS SCP service to support an "Audit" mode that would record in CloudTrail whether API calls would have been denied had the SCP not been in audit mode. This would increase customer adoption and make it easier for customers to both pilot and roll out new guardrails. (for comparison, the Azure Equivalent - Azure Policies - already [supports Audit mode](https://docs.microsoft.com/en-us/azure/governance/policy/concepts/effects#audit).
* Support the usage of `sts:AssumeRole` to prevent calls from outside your AWS Organization, with targeted exceptions.
* Add IAM Condition Keys to all the IAM Actions that are used to perform Resource Exposure. These IAM Condition Keys should be used to prevent these resources from (1) being shared with the public **and** (2) being shared outside of your `aws:PrincipalOrgPath`.
