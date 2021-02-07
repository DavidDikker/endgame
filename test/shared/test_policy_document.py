import json
import unittest
from click.testing import CliRunner
from policy_sentry.util.arns import get_account_from_arn
from endgame.shared import constants
from endgame.shared.policy_document import PolicyDocument

victim_account_id = "123456789012"
evil_principal = "arn:aws:iam::987654321:user/mwahahaha"
evil_account_id = "987654321"

policy_with_root_principal = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Sid': 'AllowCurrentAccount',
                    'Effect': 'Allow',
                    'Principal': {'AWS': 'arn:aws:iam::111222333:root'},
                    'Action': 'logs:*',
                    'Resource': ['*']
                },
                {
                    'Sid': 'Endgame',
                    'Effect': 'Allow',
                    'Principal': {'AWS': 'arn:aws:iam::999888777:root'},
                    'Action': 'logs:*',
                    'Resource': ['*']
                }
            ]
        }

policy_with_account_id = {
    'Version': '2012-10-17',
    'Statement': [
        {
            'Sid': 'AllowCurrentAccount',
            'Effect': 'Allow',
            'Principal': {'AWS': ['111222333']},
            'Action': 'logs:*',
            'Resource': ['*']
        },
        {
            'Sid': 'Endgame',
            'Effect': 'Allow',
            'Principal': {'AWS': ['999888777']},
            'Action': 'logs:*',
            'Resource': ['*']
        }
    ]
}

kms_policy = {
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
            "Action": [
                "kms:Sup"
            ],
            "Resource": [
                f"arn:aws:kms:us-east-1:123456789012:key/somekeyid",
                f"arn:aws:kms:us-east-1:123456789012:key/somekeyid/*"
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
            "Action": [
                "kms:*"
            ],
            "Resource": [
                f"arn:aws:kms:us-east-1:123456789012:key/somekeyid",
                f"arn:aws:kms:us-east-1:123456789012:key/somekeyid/*"
            ]
        }
    ]
}

ec2_assume_role_policy = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}


class PolicyDocumentTestCase(unittest.TestCase):
    def setUp(self):
        self.override_account_id_document = PolicyDocument(
            policy=kms_policy,
            service="kms",
            override_account_id_instead_of_principal=True,
            override_resource_block="*"
        )
        self.policy_with_principal_service = PolicyDocument(
            policy=ec2_assume_role_policy,
            service="iam",
            override_action="sts:AssumeRole",
            override_account_id_instead_of_principal=False,
            include_resource_block=False
        )
        self.override_action_policy = PolicyDocument(
            policy=ec2_assume_role_policy,
            service="iam",
            override_action="sts:Yolo",
            override_account_id_instead_of_principal=False,
            include_resource_block=False
        )

    def test_override_account_id_instead_of_principal(self):

        results = json.loads(self.override_account_id_document.__str__())
        allow_current_account_id = results['Statement'][0]['Principal']['AWS'][0]
        self.assertEqual(allow_current_account_id, "123456789012")
        evil_current_account_id = results['Statement'][1]['Principal']['AWS'][0]
        self.assertEqual(evil_current_account_id, "999988887777")
        # print(json.dumps(results, indent=4))

    def test_statement_with_principal_service(self):
        results = json.loads(self.policy_with_principal_service.__str__())
        print(json.dumps(results, indent=4))
        expected_results = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        self.assertDictEqual(results, expected_results)

    def test_override_action(self):
        results = json.loads(self.override_action_policy.__str__())
        print(json.dumps(results, indent=4))
        expected_results = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    },
                    "Action": "sts:Yolo"
                }
            ]
        }
        self.assertDictEqual(results, expected_results)

    def test_empty_statements(self):
        """If there are no statements, it should not break."""
        empty_statements = {
            "Version": "2012-10-17",
            "Statement": []
        }
        empty_statements_document = PolicyDocument(
            policy=empty_statements,
            service="iam",
        )
        results = json.loads(empty_statements_document.__str__())
        print(json.dumps(results, indent=4))
        self.assertDictEqual(results, empty_statements)

    def test_get_allow_current_account_id(self):
        """Allow Current account ID"""
        empty_statements = {
            "Version": "2012-10-17",
            "Statement": []
        }
        empty_statements_document = PolicyDocument(
            policy=empty_statements,
            service="iam",
            override_resource_block="*"
        )
        statement = empty_statements_document.statement_allow_account_id("999988887777", "*")
        # results = json.loads(empty_statements_document.__str__())
        print(json.dumps(statement, indent=4))
        # self.assertDictEqual(results, empty_statements)
        expected_result = {
            "Sid": "AllowCurrentAccount",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                    "arn:aws:iam::999988887777:root"
                ]
            },
            "Resource": [
                "*"
            ],
            "Action": [
                "iam:*"
            ]
        }
        self.assertEqual(statement["Resource"][0], "*")
        self.assertDictEqual(statement, expected_result)

    def test_policy_plus_evil_principal(self):
        empty_statements = {
            "Version": "2012-10-17",
            "Statement": []
        }
        empty_statements_document = PolicyDocument(
            policy=empty_statements,
            service="iam",
            override_resource_block="*",
        )
        policy = empty_statements_document.policy_plus_evil_principal(
            victim_account_id="111122223333",
            evil_principal="arn:aws:iam::999988887777:user/mwahahaha"
        )
        print(json.dumps(policy, indent=4))
        self.assertEqual(policy["Statement"][0]["Sid"], "AllowCurrentAccount")
        self.assertEqual(policy["Statement"][0]["Principal"]["AWS"][0], "arn:aws:iam::111122223333:root")
        self.assertEqual(policy["Statement"][1]["Sid"], "Endgame")
        self.assertEqual(policy["Statement"][1]["Principal"]["AWS"][0], "arn:aws:iam::999988887777:user/mwahahaha")

