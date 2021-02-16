# Detection

There are three general methods that blue teams can use to **detect** AWS Resource Exposure Attacks:

1. User Agent Detection (Endgame specific)
2. API call detection
3. Behavioral-based detection
4. AWS Access Analyzer

While (1) User Agent Detection is specific to the usage of Endgame, (2) API Call Detection, (3) Behavioral-based detection, and (4) AWS Access Analyzer are strategies to detect Resource Exposure Attacks, regardless of if the attacker is using Endgame to do it.

## Detecting Resource Exposure Attacks

### API Call Detection

Further documentation on how to query for specific API calls made to each service by endgame is available in the [risks documentation](./risks).

### Behavioral-based detection

Behavioral-based detection is currently being researched and developed by [Ryan Stalets](https://twitter.com/RyanStalets). [GitHub issue #46](https://github.com/salesforce/endgame/issues/46) is being used to track this work. We welcome all contributions and discussion!

## Detecting Endgame

### User Agent Detection

Endgame uses the user agent `HotDogsAreSandwiches` by default. While this can be overriden using the `--cloak` flag, defense teams can still use it as an IOC.

The following CloudWatch Insights query will expose events with the `HotDogsAreSandwiches` user agent in CloudTrail logs:

```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent 
| filter userAgent='HotDogsAreSandwiches'
```

This query assumes that your CloudTrail logs are being sent to CloudWatch and that you have selected the correct log group.

Further documentation on how to query for specific API calls made to each service by endgame is available in the [risks documentation](risks).

### AWS Access Analyzer

[AWS Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html) analyzes new or updated resource-based policies within 30 minutes of policy updates (triggered by CloudTrail log entries), and during periodic scans (every 24 hours). If an attacker leverages the `expose` or `smash` commands but quickly rolls back the changes with `--undo`, you might not find out about the attack with Access Analyzer until 30 minutes later.

However, Access Analyzer can still be especially useful in ensuring that if attacks do gain a foothold in your infrastructure. If the attacker ran Endgame or perform resource exposure attacks without the tool, you can still use Access Analyzer to alert on those changes so you can respond to the issue, instead of allowing a persistent backdoor.

Consider leveraging `aws:PrincipalOrgID` or `aws:PrincipalOrgPaths` in your Access Analyzer filter keys to detect access from IAM principals outside your AWS account. See [Access Analyzer Filter Keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-reference-filter-keys.html) for more details.

## Further Reading

Additional information on AWS resource policies, how this tool works in the victim account, and identification/containment suggestions is [here](resource-policy-primer.md).
