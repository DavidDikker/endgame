import json
import unittest
from click.testing import CliRunner
from policy_sentry.util.arns import get_account_from_arn
from endgame.shared import constants
from endgame.shared.policy_document import PolicyDocument
from endgame.shared.statement_detail import StatementDetail

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


class StatementDetailTestCase(unittest.TestCase):
    def test_statement_with_root(self):
        statement_detail = StatementDetail(statement=policy_with_root_principal["Statement"][0], service="logs")
        print(statement_detail.json)
        print(statement_detail.sid)
        statement_detail.sid = "OverrideSid"
        self.assertEqual(statement_detail.sid, "OverrideSid")
        print(statement_detail.sid)
        self.assertEqual(statement_detail.resources, ['*'])
        self.assertEqual(statement_detail.actions, ['logs:*'])
        self.assertEqual(statement_detail.aws_principals, ['arn:aws:iam::111222333:root'])
