# Recommendations to Blue Teams

There are three general methods that blue teams can use to detect the usage of this tool:
1. User Agent Detection
2. API call detection
3. Behavioral-based detection

## User Agent Detection

Endgame uses the user agent `HotDogsAreSandwiches` by default. While this can be overriden using the `--cloak` flag, defense teams can still use it as an IOC.

The following CloudWatch Insights query will expose events with the `HotDogsAreSandwiches` user agent in CloudTrail logs:

```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent 
| filter userAgent='HotDogsAreSandwiches'
```

This query assumes that your CloudTrail logs are being sent to CloudWatch and that you have selected the correct log group.

## API Call Detection

Further documentation on how to query for specific API calls made to each service by endgame is available in the [risks documentation](./risks/).

## Behavioral-based detection

Behavioral-based detection is currently being researched and developed by [Ryan Stalets](https://twitter.com/RyanStalets). [GitHub issue #46](https://github.com/salesforce/endgame/issues/46) is being used to track this work. We welcome all contributions and discussion!

#### Further Blue Team Reading

Additional information on AWS resource policies, how this tool works in the victim account, and identification/containment suggestions is [here](resource-policy-primer.md).