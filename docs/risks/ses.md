# SES Identity Policy

Sending authorization is based on sending authorization policies. If you want to enable a delegate sender to send on your behalf, you create a sending authorization policy and associate the policy to your identity by using the Amazon SES console or the Amazon SES API.

When Amazon SES receives the request to send the email, it checks your identity's policy (if present) to determine if you have authorized the delegate sender to send on the identity's behalf. If the delegate sender is authorized, Amazon SES accepts the email; otherwise, Amazon SES returns an error message.

This can be abused by adding a rogue user to the

## References

* [put-identity-policy](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ses/put-identity-policy.html)

* [Sending Authorization Overview](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/sending-authorization-overview.html)

* [Sending Authorization Policy Examples](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/sending-authorization-policy-examples.html)