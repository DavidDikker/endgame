# Exposure via AWS RAM

By default, AWS RAM allows you to share resources with **any** AWS Account.

Supported resource types are listed in the AWS documentation [here](https://docs.aws.amazon.com/ram/latest/userguide/shareable.html).

## Status

This exploit method is not currently implemented. Please come back later when we've implemented it.

To get notified when it is available, you can take one of the following methods:
1. In GitHub, select "Watch for new releases"
2. Follow the author [@kmcquade](https://twitter.com/kmcquade3) on Twitter. He will announce when this feature is available 😃

## Remediation

While you are able to restrict resource sharing to your organization in AWS Organizations, the only way to disable it altogether if you don't want it is to use AWS Service Control Policies.

