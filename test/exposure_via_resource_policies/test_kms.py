import unittest
import warnings
import json
from moto import mock_kms
from endgame.exposure_via_resource_policies.kms import KmsKey
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
            self.client = get_boto3_client(profile=None, service="kms", region="us-east-1")
            key_id = self.client.create_key()["KeyMetadata"]["KeyId"]
            self.client.create_alias(AliasName=MY_RESOURCE, TargetKeyId=key_id)
            self.example = KmsKey(name=MY_RESOURCE, region="us-east-1", client=self.client,
                                  current_account_id="123456789012")

    def test_get_rbp(self):
        expected_result = {
            "Version": "2012-10-17",
            "Statement": []
        }

        print(json.dumps(self.example.original_policy, indent=4))
        self.assertDictEqual(self.example.original_policy, expected_result)

    # # put_resource_policy has not been implemented by moto for kms
    # def test_set_rbp(self):
    #     evil_principal = EVIL_PRINCIPAL
    #     if evil_principal == "*":
    #         evil_account_id = "*"
    #     else:
    #         evil_account_id = get_account_from_arn(evil_principal)
    #     evil_policy = mischief.get_policy_with_evil_principal(
    #         resource_arn=self.example.arn,
    #         evil_principal=EVIL_PRINCIPAL,
    #         current_policy=self.example.policy,
    #         victim_account_id=self.example.current_account_id,
    #         include_resource_block=True,
    #         override_action=None,
    #         override_resource_block=None,
    #         evil_account_id=evil_account_id,
    #         service="kms"
    #     )
    #     # print(json.dumps(evil_policy, indent=4))
    #     results = self.example.set_rbp(evil_policy)
    #     # print(json.dumps(results, indent=4))
    #     expected_results = {
    #         "Version": "2012-10-17",
    #         "Statement": [
    #             {
    #                 "Sid": "AllowCurrentAccount",
    #                 "Effect": "Allow",
    #                 "Principal": {
    #                     "AWS": [
    #                         "arn:aws:iam::123456789012:root"
    #                     ]
    #                 },
    #                 "Action": [
    #                     "kms:*"
    #                 ],
    #                 "Resource": [
    #                     f"arn:aws:kms:us-east-1:123456789012:key/{self.example.name}",
    #                     f"arn:aws:kms:us-east-1:123456789012:key/{self.example.name}/*"
    #                 ]
    #             },
    #             {
    #                 "Sid": "Endgame",
    #                 "Effect": "Allow",
    #                 "Principal": {
    #                     "AWS": [
    #                         "arn:aws:iam::999988887777:user/evil"
    #                     ]
    #                 },
    #                 "Action": [
    #                     "kms:*"
    #                 ],
    #                 "Resource": [
    #                     f"arn:aws:kms:us-east-1:123456789012:key/{self.example.name}",
    #                     f"arn:aws:kms:us-east-1:123456789012:key/{self.example.name}/*"
    #                 ]
    #             }
    #         ]
    #     }
    #     self.assertDictEqual(results, expected_results)

    def test_add_myself(self):
        result = self.example.add_myself(evil_principal=EVIL_PRINCIPAL)
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
