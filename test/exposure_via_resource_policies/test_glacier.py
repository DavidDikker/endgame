import unittest
import warnings
import json
from moto import mock_glacier
from endgame.exposure_via_resource_policies.glacier_vault import GlacierVaults
from endgame.shared.aws_login import get_boto3_client

MY_RESOURCE = "test-resource-exposure"
EVIL_PRINCIPAL = "arn:aws:iam::999988887777:user/evil"


class GlacierTestCase(unittest.TestCase):
    def setUp(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            current_account_id = "111122223333"
            region = "us-east-1"
            service = "glacier"
            self.mock = mock_glacier()
            self.mock.start()
            self.client = get_boto3_client(profile=None, service=service, region=region)

            self.client.create_vault(vaultName=MY_RESOURCE)
            self.vaults = GlacierVaults(client=self.client, current_account_id=current_account_id, region=region)

    def test_list_vaults(self):
        print(self.vaults.resources[0].name)
        print(self.vaults.resources[0].arn)
        self.assertTrue(self.vaults.resources[0].name == "test-resource-exposure")
        self.assertTrue(self.vaults.resources[0].arn == "arn:aws:glacier:us-east-1:012345678901:vaults/test-resource-exposure")
