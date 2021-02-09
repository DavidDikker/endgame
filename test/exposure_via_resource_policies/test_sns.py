import unittest
import warnings
import json
from moto import mock_sns
from endgame.exposure_via_resource_policies.sns import SnsTopic, SnsTopics
from endgame.shared.aws_login import get_boto3_client
from endgame.shared import constants

MY_RESOURCE = "test-resource-exposure"
EVIL_PRINCIPAL = "arn:aws:iam::999988887777:user/evil"


# https://github.com/spulec/moto/blob/master/tests/test_sns/test_topics.py
class SnsTestCase(unittest.TestCase):
    def setUp(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            self.mock = mock_sns()
            self.mock.start()
            current_account_id = "123456789012"
            region = "us-east-1"
            self.client = get_boto3_client(profile=None, service="sns", region=region)
            response = self.client.create_topic(Name=MY_RESOURCE)
            self.example = SnsTopic(name=MY_RESOURCE, region=region, client=self.client,
                                    current_account_id=current_account_id)
            self.topics = SnsTopics(client=self.client, current_account_id=current_account_id, region=region)

    def test_list_topics(self):
        print(self.topics.resources[0].name)
        print(self.topics.resources[0].arn)
        self.assertTrue(self.topics.resources[0].name == "test-resource-exposure")
        self.assertTrue(self.topics.resources[0].arn == "arn:aws:sns:us-east-1:123456789012:test-resource-exposure")


    def test_get_rbp(self):
        # This is the default policy
        expected_result = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Sid": "__default_statement_ID",
                    "Principal": {
                        "AWS": "*"
                    },
                    "Action": [
                        "SNS:GetTopicAttributes",
                        "SNS:SetTopicAttributes",
                        "SNS:AddPermission",
                        "SNS:RemovePermission",
                        "SNS:DeleteTopic",
                        "SNS:Subscribe",
                        "SNS:ListSubscriptionsByTopic",
                        "SNS:Publish",
                        "SNS:Receive"
                    ],
                    "Resource": "arn:aws:sns:us-east-1:123456789012:test-resource-exposure",
                    "Condition": {
                        "StringEquals": {
                            "AWS:SourceOwner": "123456789012"
                        }
                    }
                }
            ]
        }
        print(json.dumps(self.example.original_policy, indent=4))
        self.maxDiff = None
        self.assertDictEqual(self.example.original_policy, expected_result)

    def test_set_rbp(self):
        example_sns_policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Sid": "grant-1234-publish",
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"{EVIL_PRINCIPAL}"
                },
                "Action": ["sns:Publish"],
                "Resource": f"arn:aws:sns:us-east-2:111122223333:{MY_RESOURCE}"
            }]
        }
        expected_results = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "__default_statement_ID",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": [
                            "*"
                        ]
                    },
                    "Resource": [
                        "arn:aws:sns:us-east-1:123456789012:test-resource-exposure"
                    ],
                    "Action": [
                        "sns:AddPermission",
                        "sns:DeleteTopic",
                        "sns:GetTopicAttributes",
                        "sns:ListSubscriptionsByTopic",
                        "sns:Publish",
                        "sns:Receive",
                        "sns:RemovePermission",
                        "sns:SetTopicAttributes",
                        "sns:Subscribe"
                    ],
                    "Condition": {
                        "StringEquals": {
                            "AWS:SourceOwner": "123456789012"
                        }
                    }
                },
                {
                    "Sid": "grant-1234-publish",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": [
                            "999988887777"
                        ]
                    },
                    "Resource": [
                        "arn:aws:sns:us-east-1:123456789012:test-resource-exposure"
                    ],
                    "Action": [
                        "sns:AddPermission",
                        "sns:DeleteTopic",
                        "sns:GetTopicAttributes",
                        "sns:ListSubscriptionsByTopic",
                        "sns:Publish",
                        "sns:Receive",
                        "sns:RemovePermission",
                        "sns:SetTopicAttributes",
                        "sns:Subscribe"
                    ]
                }
            ]
        }
        response = self.example.set_rbp(example_sns_policy)
        print(json.dumps(response.updated_policy, indent=4))
        self.assertDictEqual(response.updated_policy, expected_results)

    def test_set_rbp_by_removal(self):
        print(json.dumps(self.example.original_policy, indent=4))
        results = self.example.add_myself(evil_principal=EVIL_PRINCIPAL)
        print(json.dumps(results.updated_policy, indent=4))

    def test_add_myself(self):
        result = self.example.add_myself(evil_principal=EVIL_PRINCIPAL)
        self.assertListEqual(result.updated_policy_sids, ["__default_statement_ID", 'AllowCurrentAccount', f"{constants.SID_SIGNATURE}"])

    def test_undo(self):
        result = self.example.add_myself(evil_principal=EVIL_PRINCIPAL)
        print(result.updated_policy_sids)
        undo_result = self.example.undo(evil_principal=EVIL_PRINCIPAL)
        print(undo_result.updated_policy_sids)
        self.assertListEqual(result.updated_policy_sids, ["__default_statement_ID", 'AllowCurrentAccount', f"{constants.SID_SIGNATURE}"])

    def tearDown(self):
        self.client.delete_topic(TopicArn=self.example.arn)
        self.mock.stop()
