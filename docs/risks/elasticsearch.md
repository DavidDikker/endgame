# ElasticSearch Domains


## Vulnerable config

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "es:*",
      "Resource": "arn:aws:es:us-east-1:999988887777:domain/test-resource-exposure/*"
    }
  ]
}
```

## References

* [ElasticSearch Resource-based Policies](https://docs.aws.amazon.com/elasticsearch-service/latest/developerguide/es-ac.html#es-ac-types-resource)