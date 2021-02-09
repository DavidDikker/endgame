import unittest
import warnings
import json
from moto import mock_secretsmanager
from endgame.exposure_via_resource_policies.secrets_manager import SecretsManagerSecret, SecretsManagerSecrets
from endgame.shared.aws_login import get_boto3_client

MY_RESOURCE = "test-resource-exposure"
EVIL_PRINCIPAL = "arn:aws:iam::999988887777:user/evil"


# https://github.com/spulec/moto/blob/master/tests/test_secretsmanager/test_secretsmanager.py
class SecretsManagerTestCase(unittest.TestCase):
    def setUp(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            self.mock = mock_secretsmanager()
            self.mock.start()
            current_account_id = "111122223333"
            region = "us-east-1"
            self.client = get_boto3_client(profile=None, service="secretsmanager", region=region)
            response = self.client.create_secret(
                Name=MY_RESOURCE, SecretString="foosecret"
            )
            self.example = SecretsManagerSecret(name=MY_RESOURCE, region=region, client=self.client,
                                                current_account_id=current_account_id)
            self.secrets = SecretsManagerSecrets(client=self.client, current_account_id=current_account_id, region=region)

    def test_list_secrets(self):
        print(self.secrets.resources[0].name)
        print(self.secrets.resources[0].arn)
        self.assertTrue(self.secrets.resources[0].name == "test-resource-exposure")
        self.assertTrue(self.secrets.resources[0].arn.startswith("arn:aws:secretsmanager:us-east-1:1234567890:secret:test-resource-exposure"))

    def test_get_rbp(self):
        expected_result = {
            "Version": "2012-10-17",
            "Statement": {
                "Effect": "Allow",
                "Principal": {
                    "AWS": [
                        "arn:aws:iam::111122223333:root",
                        "arn:aws:iam::444455556666:root"
                    ]
                },
                "Action": [
                    "secretsmanager:GetSecretValue"
                ],
                "Resource": "*"
            }
        }
        print(json.dumps(self.example.original_policy, indent=4))
        self.assertDictEqual(self.example.original_policy, expected_result)

    # put_resource_policy has not been implemented by moto for secrets manager
    # def test_set_rbp(self):
    # def test_add_myself(self):

    def tearDown(self):
        self.client.delete_secret(SecretId=MY_RESOURCE)
        self.mock.stop()
