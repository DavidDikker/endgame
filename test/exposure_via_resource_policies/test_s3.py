import unittest
import warnings
from moto import mock_s3
from endgame.exposure_via_resource_policies import s3
from endgame.shared.aws_login import get_boto3_client
from endgame.shared import constants

MY_RESOURCE = "mybucket"
EVIL_PRINCIPAL = "arn:aws:iam::999988887777:user/evil"


class S3TestCase(unittest.TestCase):
    def setUp(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            self.mock = mock_s3()
            self.mock.start()
            region = "us-east-1"
            current_account_id = "123456789012"
            self.client = get_boto3_client(profile=None, service="s3", region=region)
            self.client.create_bucket(Bucket=MY_RESOURCE)
            self.example = s3.S3Bucket(name=MY_RESOURCE, region=region, client=self.client,
                                       current_account_id=current_account_id)
            self.buckets = s3.S3Buckets(client=self.client, current_account_id=current_account_id, region=region)

    def test_list_roles(self):
        print(self.buckets.resources[0].name)
        self.assertTrue(self.buckets.resources[0].arn == "arn:aws:s3:::mybucket")
        self.assertTrue(self.buckets.resources[0].name == "mybucket")

    def test_get_rbp(self):
        expected_result = {'Version': '2012-10-17', 'Statement': []}
        self.assertDictEqual(self.example.original_policy, expected_result)

    def test_set_rbp(self):
        before = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    "Sid": "Yolo",
                    "Effect": "Allow",
                    "Principal": {"AWS": [f"arn:aws:iam::999988887777:user/canttouchthis"]},
                    "Action": "*:*",
                    "Resource": "*:*",
                }
            ]
        }
        after = self.example.set_rbp(before)
        self.assertDictEqual(before, after.updated_policy)

    def test_add_myself(self):
        result = self.example.add_myself(evil_principal=EVIL_PRINCIPAL)
        self.assertListEqual(result.updated_policy_sids, [constants.ALLOW_CURRENT_ACCOUNT_SID_SIGNATURE, f"{constants.SID_SIGNATURE}"])

    def tearDown(self):
        self.client.delete_bucket(Bucket=MY_RESOURCE)
        self.mock.stop()
