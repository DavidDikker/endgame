import unittest
import warnings
import json
from moto import mock_ses
from endgame.exposure_via_resource_policies.ses import SesIdentityPolicies
from endgame.shared.aws_login import get_boto3_client
from endgame.shared import constants

MY_RESOURCE = "test-resource-exposure@yolo.com"
EVIL_PRINCIPAL = "arn:aws:iam::999988887777:user/evil"


class SesTestCase(unittest.TestCase):
    def setUp(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            current_account_id = "111122223333"
            region = "us-east-1"
            service = "ses"
            self.mock = mock_ses()
            self.mock.start()
            self.client = get_boto3_client(profile=None, service=service, region=region)
            response = self.client.verify_email_identity(
                EmailAddress=MY_RESOURCE
            )
            print(response)
            self.identities = SesIdentityPolicies(client=self.client, current_account_id=current_account_id, region=region)

    def test_list_identities(self):
        print(self.identities.resources[0].name)
        print(self.identities.resources[0].arn)
        self.assertTrue(self.identities.resources[0].name == MY_RESOURCE)
        self.assertTrue(self.identities.resources[0].arn == f"arn:aws:ses:us-east-1:111122223333:identity/{MY_RESOURCE}")
