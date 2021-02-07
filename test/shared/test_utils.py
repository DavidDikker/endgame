import json
import unittest
from click.testing import CliRunner
from policy_sentry.util.arns import get_account_from_arn
from endgame.shared import constants
from endgame.shared.utils import change_policy_principal_from_arn_to_account_id

victim_account_id = "123456789012"
evil_principal = "arn:aws:iam::987654321:user/mwahahaha"
evil_account_id = "987654321"


class ChangePrincipalArnToIdTestCase(unittest.TestCase):
    def test_principal_is_string(self):
        print()
        policy = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Sid': 'AllowCurrentAccount',
                    'Effect': 'Allow',
                    'Principal': {'AWS': 'arn:aws:iam::111222333:root'},
                    'Action': 'logs:*',
                    'Resource': ['*', '*/*']
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
        expected_result = {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Sid': 'AllowCurrentAccount',
                    'Effect': 'Allow',
                    'Principal': {'AWS': ['111222333']},
                    'Action': 'logs:*',
                    'Resource': ['*', '*/*']
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
        results = change_policy_principal_from_arn_to_account_id(policy)
        print(json.dumps(results, indent=4))
        self.assertDictEqual(results, expected_result)

    def test_principal_is_list(self):
        print()

    # def test_principal_does_not_exist(self):
    #     print()
