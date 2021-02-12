# Moto support status per service

* ACM PCA: ❌ Not supported by Moto
  * `delete_policy`: ❌ Not supported
  * `get_policy`: ❌ Not supported
  * `list_certificate_authorities`: ❌ Not supported
  * `put_policy`: ❌ Not supported
* CloudWatch Logs: ❌ Resource policy not supported by Moto
  * `describe_resource_policies`: ❌ Not supported
  * `delete_resource_policy`: ❌ Not supported
  * `put_resource_policy`: ❌ Not supported
* ECR
  * `describe_repositories`: ✅ Supported
  * `delete_repository_policy`: ❌ Not supported
  * `get_repository_policy`: ❌ Not supported ⁉️
  * `set_repository_policy`: ❌ Not supported
* EFS: ❌ Not supported by Moto
  * `describe_file_system_policy`: ❌ Not supported
  * `describe_file_systems`: ❌ Not supported
  * `put_file_system_policy`: ❌ Not supported
* ElasticSearch: ❌ Not supported by Moto
  * `describe_elasticsearch_domain_config`: Not supported
  * `list_domain_names`: Not supported
  * `update_elasticsearch_domain_config`: Not supported
* Glacier Vault
  * `get_vault_access_policy`: ❌ Not supported
  * `list_vaults`: ❌ Not supported ⁉️
  * `set_vault_access_policy`: ❌ Not supported
* IAM
  * `get_role`: ✅ Supported
  * `list_roles`: ✅ Supported
  * `update_assume_role_policy`: ✅ Supported
* KMS
  * `get_key_policy`: ✅ Supported
  * `list_keys`: ✅ Supported
  * `list_aliases`: ❌ Not supported ⁉️
  * `put_key_policy`: ✅ Supported
* Lambda Function
  * `list_functions`: ✅ Supported
  * `get_function_policy`: ✅ Supported
  * `add_permission`: ✅ Supported
  * `remove_permission`: ✅ Supported
* Lambda Layer:
  * `list_layers`: ✅ Supported
  * `list_layer_versions`: ❌ Not supported
  * `add_layer_version_permission`: ❌ Not supported
  * `remove_layer_version_permission`: ❌ Not supported
* S3:
  * `get_bucket_policy`: ✅ Supported
  * `put_bucket_policy`: ✅ Supported
  * `list_buckets`: ✅ Supported
* Secrets Manager
  * `delete_resource_policy`: ❌ Not supported
  * `get_resource_policy`: ✅ Supported
  * `list_secrets`: ✅ Supported
  * `put_resource_policy`: ❌ Not supported
* SES
  * `delete_identity_policy`: ❌ Not supported
  * `get_identity_policies`: ❌ Not supported
  * `list_identities`: ✅ Supported
  * `list_identity_policies`: ❌ Not supported
  * `put_identity_policy`: ❌ Not supported
* SNS
  * `add_permission`: ✅ Supported
  * `get_topic_attributes`: ✅ Supported
  * `remove_permission`: ✅ Supported
  * `list_topics`: ✅ Supported
* SQS
  * `add_permission`: ✅ Supported
  * `get_queue_url`: ✅ Supported
  * `get_queue_attributes`: ✅ Supported
  * `list_queues`: ✅ Supported
  * `remove_permission`: ✅ Supported

## Unit test structure per service

We want to cover the following in each unit test:
* `setUp`
* `test_list_resources`
  * Passing case: If exists, assert name is expected
  * Exception handling: If does not exist, show error message but don't break
* `test_get_rbp`
  * Expected initial policy content
* `test_set_rbp`
  * Expected policy content after updating
  * Exception handling in case of `botocore.exceptions.ClientError`
* `test_add_myself`
  * Expected policy content after updating
  * Exception handling in case of `botocore.exceptions.ClientError`
* `tearDown`

## Notes

[ECR](https://github.com/spulec/moto/blob/master/tests/test_ecr/test_ecr_boto3.py): 🟡 Partially supported. `test_get_rbp` possible

[Glacier Vault](https://github.com/spulec/moto/tree/master/tests/test_glacier). Looks like `list_vaults` is under `mock_glacier_deprecated`

[KMS](https://github.com/spulec/moto/blob/9db62d32bf70e18f315305b7915d199e3ba1210a/tests/test_kms/test_kms.py#L269): ✅ possible. TODO: Need to update with `put_key_policy` from `mock_kms_deprecated`

[IAM](https://github.com/spulec/moto/blob/fe9f1dfe140a8f52746b964df121ae1a13fdf93d/moto/iam/responses.py#L253)