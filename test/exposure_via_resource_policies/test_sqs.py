import unittest
import warnings
import json
from moto import mock_sqs
from endgame.exposure_via_resource_policies.sqs import SqsQueue, SqsQueues
from endgame.shared.aws_login import get_boto3_client
from endgame.shared import constants

MY_RESOURCE = "test-resource-exposure"
EVIL_PRINCIPAL = "arn:aws:iam::999988887777:user/evil"


# https://github.com/spulec/moto/blob/master/tests/test_sqs/test_sqs.py
class SqsTestCase(unittest.TestCase):
    def setUp(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            self.mock = mock_sqs()
            self.mock.start()
            current_account_id = "123456789012"
            region = "us-east-1"
            self.client = get_boto3_client(profile=None, service="sqs", region=region)
            self.queue_url = self.client.create_queue(QueueName=MY_RESOURCE)["QueueUrl"]
            self.example = SqsQueue(name=MY_RESOURCE, region=region, client=self.client,
                                    current_account_id=current_account_id)
            self.queues = SqsQueues(client=self.client, current_account_id=current_account_id, region=region)

    def test_list_queues(self):
        print(self.queues.resources[0].name)
        print(self.queues.resources[0].arn)
        self.assertTrue(self.queues.resources[0].name == "test-resource-exposure")
        self.assertTrue(self.queues.resources[0].arn.startswith("arn:aws:sqs:us-east-1:123456789012:test-resource-exposure"))

    def test_get_rbp(self):
        # response = self.client.get_queue_attributes(QueueUrl=self.queue_url)
        queue_arn = self.client.get_queue_attributes(QueueUrl=self.queue_url)["Attributes"]["QueueArn"]
        # actual_policy = self.client.get_queue_attributes(QueueUrl=self.queue_url, AttributeNames=["Policy"])
        print(queue_arn)
        expected_original_policy = {
            "Version": "2012-10-17",
            "Statement": []
        }
        print(json.dumps(self.example.original_policy, indent=4))
        self.assertDictEqual(self.example.original_policy, expected_original_policy)

    def test_set_rbp(self):
        expected_results = {
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
                    "Resource": [
                        "arn:aws:sqs:us-east-1:123456789012:test-resource-exposure"
                    ],
                    "Action": [
                        "sqs:*"
                    ]
                },
                {
                    "Sid": "Endgame",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": [
                            "arn:aws:iam::999988887777:root"
                        ]
                    },
                    "Resource": [
                        "arn:aws:sqs:us-east-1:123456789012:test-resource-exposure"
                    ],
                    "Action": [
                        "sqs:*"
                    ]
                }
            ]
        }
        response = self.example.set_rbp(evil_policy=expected_results)
        # print(json.dumps(results, indent=4))
        self.maxDiff = None
        self.assertDictEqual(response.updated_policy, expected_results)

    def test_add_myself(self):
        result = self.example.add_myself(evil_principal=EVIL_PRINCIPAL)
        print(result.updated_policy_sids)
        self.assertListEqual(result.updated_policy_sids, ["AllowCurrentAccount", f"{constants.SID_SIGNATURE}"])

    def test_undo(self):
        add_myself_result = self.example.add_myself(evil_principal=EVIL_PRINCIPAL)
        print(add_myself_result.updated_policy_sids)
        result = self.example.undo(evil_principal=EVIL_PRINCIPAL)
        print(result.updated_policy_sids)
        self.assertListEqual(result.updated_policy_sids, ["AllowCurrentAccount"])

    def tearDown(self):
        self.client.delete_queue(QueueUrl=self.example.queue_url)
        self.mock.stop()
