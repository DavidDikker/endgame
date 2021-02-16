# FAQ

## Where does AWS Access Analyzer fall short?

[AWS Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html) analyzes new or updated resource-based policies within 30 minutes of policy updates (triggered by CloudTrail log entries), and during periodic scans (every 24 hours). If an attacker leverages the `expose` or `smash` commands but quickly rolls back the changes with `--undo`, you might not find out about the attack with Access Analyzer until 30 minutes later.

However, Access Analyzer can still be especially useful in ensuring that if attacks do gain a foothold in your infrastructure. If the attacker ran Endgame or perform resource exposure attacks without the tool, you can still use Access Analyzer to alert on those changes so you can respond to the issue, instead of allowing a persistent backdoor.

The primary drawback with AWS Access Analyzer is that it does not support 11/17 resource types currently supported by Endgame. It also does not support AWS RAM Resource sharing outside of your trust zone, or resource-specific sharing APIs (such as RDS snapshots, EBS snapshots, and EC2 AMIs).

See the [Recommendations to AWS](../recommendations-to-aws.md) section for more details.

## Related Tools in the Ecosystem

### Attack tools

[Pacu](https://github.com/RhinoSecurityLabs/pacu/) is an AWS exploitation framework created by [Spencer Gietzen](https://twitter.com/SpenGietz), designed for testing the security of Amazon Web Services environments. The [iam__backdoor_assume_role](https://github.com/RhinoSecurityLabs/pacu/blob/master/modules/iam__backdoor_assume_role/main.py) module was a particular point of inspiration for `endgame` - it creates backdoors in IAM roles by creating trust relationships with one or more roles in the account, allowing those users to assume those roles after they are no longer using their current set of credentials.

### Detection/scanning tools

[Cloudsplaining](https://opensource.salesforce.com/cloudsplaining/), is an AWS IAM assessment tool produced by [Kinnaird McQuade](https://twitter.com/kmcquade3) that showed us the pervasiveness of least privilege violations in AWS IAM across the industry. Two findings of particular interest to `endgame` are Resource Exposure and Service Wildcards. Resource Exposure describes actions that grant access to share resources with rogue accounts or to the internet - i.e., modifying Resource-based Policies, sharing resources with AWS RAM, or via resource-specific sharing APIs (such as RDS snapshots, EBS snapshots, or EC2 AMIs).

### Prevention tools

[Policy Sentry](https://engineering.salesforce.com/salesforce-cloud-security-automating-least-privilege-in-aws-iam-with-policy-sentry-b04fe457b8dc) is a least-privilege
 IAM Authoring tool created by [Kinnaird McQuade](https://twitter.com/kmcquade3) that demonstrated to the industry how to write least privilege IAM policies at scale, restricting permissions according to specific resources and access levels.
