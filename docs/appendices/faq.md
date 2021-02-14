# FAQ

## Related Tools in the Ecosystem

### Attack tools

[Pacu](https://github.com/RhinoSecurityLabs/pacu/) is an AWS exploitation framework created by [Spencer Gietzen](https://twitter.com/SpenGietz), designed for testing the security of Amazon Web Services environments. The [iam__backdoor_assume_role](https://github.com/RhinoSecurityLabs/pacu/blob/master/modules/iam__backdoor_assume_role/main.py) module was a particular point of inspiration for `endgame` - it creates backdoors in IAM roles by creating trust relationships with one or more roles in the account, allowing those users to assume those roles after they are no longer using their current set of credentials.

### Detection/scanning tools

[Cloudsplaining](https://opensource.salesforce.com/cloudsplaining/), is an AWS IAM assessment tool produced by [Kinnaird McQuade](https://twitter.com/kmcquade3) that showed us the pervasiveness of least privilege violations in AWS IAM across the industry. Two findings of particular interest to `endgame` are Resource Exposure and Service Wildcards. Resource Exposure describes actions that grant access to share resources with rogue accounts or to the internet - i.e., modifying Resource-based Policies, sharing resources with AWS RAM, or via resource-specific sharing APIs (such as RDS snapshots, EBS snapshots, or EC2 AMIs).

### Prevention tools

[Policy Sentry](https://engineering.salesforce.com/salesforce-cloud-security-automating-least-privilege-in-aws-iam-with-policy-sentry-b04fe457b8dc) is a least-privilege
 IAM Authoring tool created by [Kinnaird McQuade](https://twitter.com/kmcquade3) that demonstrated to the industry how to write least privilege IAM policies at scale, restricting permissions according to specific resources and access levels.
