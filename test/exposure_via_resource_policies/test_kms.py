import unittest
import warnings
import json
from moto import mock_kms
from endgame.exposure_via_resource_policies.kms import KmsKey, KmsKeys
from endgame.shared.aws_login import get_boto3_client
from endgame.shared import constants

MY_RESOURCE = "alias/test-resource-exposure"
EVIL_PRINCIPAL = "arn:aws:iam::999988887777:user/evil"


# https://github.com/spulec/moto/blob/master/tests/test_sqs/test_sqs.py
class KmsTestCase(unittest.TestCase):
    def setUp(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            self.mock = mock_kms()
            self.mock.start()
            region = "us-east-1"
            current_account_id = "123456789012"
            self.client = get_boto3_client(profile=None, service="kms", region=region)
            self.key_id = self.client.create_key()["KeyMetadata"]["KeyId"]
            self.client.create_alias(AliasName=MY_RESOURCE, TargetKeyId=self.key_id)
            self.example = KmsKey(name=MY_RESOURCE, region=region, client=self.client,
                                  current_account_id=current_account_id)
            self.keys = KmsKeys(client=self.client, current_account_id=current_account_id, region=region)

    def test_list_keys(self):
        print(self.keys.resources[0].name)
        print(self.keys.resources[0].arn)
        self.assertTrue(self.keys.resources[0].name == self.key_id)
        self.assertTrue(self.keys.resources[0].arn == f"arn:aws:kms:us-east-1:123456789012:key/{self.key_id}")

    def test_get_rbp(self):
        expected_result = {
            "Version": "2012-10-17",
            "Statement": []
        }

        print(json.dumps(self.example.original_policy, indent=4))
        self.assertDictEqual(self.example.original_policy, expected_result)

    def test_add_myself(self):
        result = self.example.add_myself(evil_principal=EVIL_PRINCIPAL)
        print(json.dumps(result.updated_policy, indent=4))
        """Example output:
        {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCurrentAccount",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                    "arn:aws:iam::123456789012:root"
                ]
            },
            "Resource": "arn:aws:kms:us-east-1:123456789012:key/55444291-fd1f-48b5-93c1-dcb37f305b82",
            "Action": [
                "kms:*"
            ]
        },
        {
            "Sid": "Endgame",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                    "arn:aws:iam::999988887777:user/evil"
                ]
            },
            "Resource": "arn:aws:kms:us-east-1:123456789012:key/55444291-fd1f-48b5-93c1-dcb37f305b82",
            "Action": [
                "kms:*"
            ]
        }
    ]
}
        """
        self.assertListEqual(result.updated_policy_sids, ["AllowCurrentAccount", f"{constants.SID_SIGNATURE}"])

    def test_undo(self):
        result = self.example.add_myself(evil_principal=EVIL_PRINCIPAL)
        print(result.updated_policy_sids)
        self.assertListEqual(result.updated_policy_sids,  ["AllowCurrentAccount", f"{constants.SID_SIGNATURE}"])
        result = self.example.undo(evil_principal=EVIL_PRINCIPAL)
        print(result.updated_policy_sids)
        self.assertListEqual(result.updated_policy_sids, ["AllowCurrentAccount"])

    def tearDown(self):
        self.client.schedule_key_deletion(KeyId=self.example.name)
        self.mock.stop()
