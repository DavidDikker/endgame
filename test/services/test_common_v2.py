import unittest
from abc import ABC
from endgame.exposure_via_resource_policies.common import ResourceType
from endgame.shared.aws_login import get_boto3_client
import boto3
from moto import mock_s3
import warnings
import json
import logging
from endgame.shared import constants
import botocore
from botocore.exceptions import ClientError
from endgame.shared.policy_document import PolicyDocument

logger = logging.getLogger(__name__)


class ResourceTypeV2ImplementationExample(ResourceType, ABC):
    def __init__(self, name: str, region: str, client: boto3.Session.client, current_account_id: str):
        service = "s3"
        resource_type = "bucket"
        super().__init__(name, resource_type, service, region, client, current_account_id)

    @property
    def arn(self) -> str:
        return f"arn:aws:s3:::{self.name}"

    def _get_rbp(self) -> PolicyDocument:
        """Get the resource based policy for this resource and store it"""
        try:
            response = self.client.get_bucket_policy(Bucket=self.name)
            policy = json.loads(response.get("Policy"))
        except botocore.exceptions.ClientError:
            # This occurs when there is no resource policy attached
            # So let's return a policy that won't break anything but we can add our malicious statement onto
            policy = constants.get_empty_policy()
        policy_document = PolicyDocument(
            policy=policy,
            service=self.service,
            override_action=self.override_action,
            include_resource_block=self.include_resource_block,
            override_resource_block=self.override_resource_block,
            override_account_id_instead_of_principal=self.override_account_id_instead_of_principal,
        )
        return policy_document

    def set_rbp(self, evil_policy: dict) -> dict:
        new_policy = json.dumps(evil_policy)
        self.client.put_bucket_policy(Bucket=self.name, Policy=new_policy)
        return evil_policy


MY_BUCKET = "mybucket"


class CommonResourceTypeV2TestCase(unittest.TestCase):

    def setUp(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            self.mock = mock_s3()
            self.mock.start()
            self.client = get_boto3_client(profile=None, service="s3", region="us-east-1")
            self.client.create_bucket(Bucket=MY_BUCKET)
            self.example_s3 = ResourceTypeV2ImplementationExample(name=MY_BUCKET, region="us-east-1", client=self.client,
                                                                current_account_id="111122223333")

    def test_common_implementation(self):
        """services.common.ResourceType testing"""
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            self.assertTrue(self.example_s3.arn == "arn:aws:s3:::mybucket")

    def test_get_original_rbp(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            expected_result = {'Version': '2012-10-17', 'Statement': []}
            self.assertDictEqual(self.example_s3.original_policy, expected_result)

    def test_set_rbp(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
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
            after = self.example_s3.set_rbp(before)
            # print(json.dumps(after, indent=4))
            self.assertDictEqual(before, after)

    def test_add_myself(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            empty_policy = {'Version': '2012-10-17', 'Statement': []}
            after = self.example_s3.set_rbp(evil_policy=empty_policy)
            self.assertDictEqual(empty_policy, after)
            evil_principal = "arn:aws:iam::999988887777:user/evil"
            result = self.example_s3.add_myself(evil_principal=evil_principal)
            # print(json.dumps(result, indent=4))
            expected_result = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": constants.ALLOW_CURRENT_ACCOUNT_SID_SIGNATURE,
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": [
                                "arn:aws:iam::111122223333:root"
                            ]
                        },
                        "Action": [
                            "s3:*"
                        ],
                        "Resource": [
                            "arn:aws:s3:::mybucket",
                            "arn:aws:s3:::mybucket/*"
                        ]
                    },
                    {
                        "Sid": f"{constants.SID_SIGNATURE}",
                        "Effect": "Allow",
                        "Principal": {
                            "AWS": [
                                "arn:aws:iam::999988887777:user/evil"
                            ]
                        },
                        "Action": [
                            "s3:*"
                        ],
                        "Resource": [
                            "arn:aws:s3:::mybucket",
                            "arn:aws:s3:::mybucket/*"
                        ]
                    }
                ]
            }
            self.assertDictEqual(result.updated_policy, expected_result)

    def tearDown(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            self.client.delete_bucket(Bucket=MY_BUCKET)
            self.mock.stop()
