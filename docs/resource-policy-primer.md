# AWS Resource Policies, Endgame, and You
## Background
AWS resource policies enable developers to grant permissions to specified principals (or the internet) using policy documents that apply only to a specific resource (ex: buckets, KMS keys, etc). This enables very granular access to resources to be achieved. For example, you can grant an IAM user in another account very specific permissions to a single S3 bucket without requiring them to assume a role in your account.

## Identity Policies vs. Resource Policies
The key thing to remember with resource-based policies is that they are attached _directly to an AWS resource_, like an S3 bucket, and are considered as one component in the policy evaluation that occurs when an API call is made. They are managed _by the service itself_, not IAM. Identity-based policies are attached to _an IAM principal_ such as an IAM user or role. These policies define what a principal can do across all services and resources; however, they do not always limit what permissions can be granted to the principal by a resource-based policy.

## Policy Evaluation Process
In the context of Endgame, the most important process to understand is the one documented [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic-cross-account.html). This process defines how resource policies and identity policies interact when _cross-account_ calls are made to a resource, which is the most likely scenario for an Endgame victim. To summarize the document, when the principal making the API call is in a different account than the resource the call targets, both the identity policy of the calling principal and the resource policy of the subject resource must permit the call (this is different than when the principal and resource are in the same account). Endgame exploits the fact that since the attacker controls their own account, access to a resource in a victim account can be granted using the resource policy alone.

## What This Means for Defenders
### How Endgame Works
The prerequisite for an attacker running Endgame is they have access to AWS API credentials for the victim account which have privileges to update resource policies.

Endgame can run in two modes, ```expose``` or ```smash```. The less-destructive ```expose``` mode is surgical, updating the resource policy on a single attacker-defined resource to include a back door to a principal they control (or the internet if they're mean).

```smash```, on the other hand, is more destructive (and louder). ```smash``` can run on a single service or all supported services. In either case, for each service it enumerates a list of resources in that region, reads the current resource policy on each, and applies a new policy which includes the "evil principal" the attacker has specified. The net effect of this is that depending on the privileges they have in the victim account, an attacker can insert dozens of back doors which are not controlled by the victim's IAM policies. 

These back doors largely grant access to accomplish data exfiltration from buckets, snapshots, etc. However, other things could be possible depending on the victim account's architecture. For example, an attacker could use these back doors to:

* Escalate privileges by enabling the attacker's evil principal to assume roles in the victim account
* Manipulate CI/CD pipelines which rely on AWS S3 as an artifact source
* Modify Lambda functions to include back doors, skimmers, etc for Lambda-based serverless applications
* Invoke Lambda functions with unfiltered input, bypassing API Gateway for serverless API's
* Provide attacker-defined input to applications which leverage SQS or SNS for work control
* Pivot to other applications which have credentials stored in Secrets Manager
* And more!

### Incident Identification & Containment Steps
In incidents where resource policies may have been modified (can be determined using CloudTrail, see [risks](/docs/risks/)), each resource policy should be reviewed to identify potential back doors or unintended internet exposure. The attacker's interactions with these resources should also be reviewed where possible. 

CloudTrail only logs data-level events (S3 object retrieval, Lambda function invocation, etc) for three services: S3, Lambda, and KMS. This visibility is also not enabled by default on trails. Other management-level events such as manipulation of Lambda function code will be visible in a standard management-event CloudTrail trail. Further documentation for working with CloudTrail can be found [here](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-getting-started.html).