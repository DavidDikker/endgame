### Backdoors via AWS Resource Access Manager

By default, AWS RAM allows you to share resources with **any** AWS Account.

Supported resource types are listed in the AWS documentation [here](https://docs.aws.amazon.com/ram/latest/userguide/shareable.html).

## Status

This exploit method is not currently implemented. Please come back later when we've implemented it.

To get notified when it is available, you can take one of the following methods:
1. In GitHub, select "Watch for new releases"
2. Follow the author [@kmcquade](https://twitter.com/kmcquade3) on Twitter. He will announce when this feature is available 😃

### Resources not on roadmap

| Resource Type                 | Support Status |
|-------------------------------|----------------|
| S3 Objects                    | ❌             |
| CloudWatch Destinations       | ❌             |
| Glue                          | ❌             |

* **S3 Buckets**: We do not plan on sharing individual S3 objects given the sheer amount of bandwidth that would require. If you want this feature, I suggest scripting it.
* **CloudWatch Destinations**: Modifying CloudWatch destination policies would only provide the benefit of delivering victim logs to attacker accounts - but that would have to be open permanently. This is not as destructive or useful to an attacker as the rest of these exploits, so I am not including it here.
* **Glue**: According to the [AWS documentation on AWS Glue Resource Policies](https://docs.aws.amazon.com/glue/latest/dg/glue-resource-policies.html), _"An AWS Glue resource policy can only be used to manage permissions for Data Catalog resources. You can't attach it to any other AWS Glue resources such as jobs, triggers, development endpoints, crawlers, or classifiers"_. This kind of data access is not as useful as destructive actions, at first glance. We are open to supporting this resource, but on pull requests only.
