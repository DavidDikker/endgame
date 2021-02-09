import unittest
import warnings
import json
from moto import mock_iam
from endgame.exposure_via_resource_policies.iam import IAMRole, IAMRoles
from endgame.shared.aws_login import get_boto3_client
from endgame.shared import constants

MY_RESOURCE = "test-resource-exposure"
EVIL_PRINCIPAL = "arn:aws:iam::999988887777:user/evil"


class IAMTestCase(unittest.TestCase):
    def setUp(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            current_account_id = "111122223333"
            region = "us-east-1"
            self.mock = mock_iam()
            self.mock.start()
            self.client = get_boto3_client(profile=None, service="iam", region=region)

            self.client.create_role(RoleName=MY_RESOURCE, AssumeRolePolicyDocument=json.dumps(constants.EC2_ASSUME_ROLE_POLICY))
            self.example = IAMRole(name=MY_RESOURCE, region=region, client=self.client,
                                   current_account_id=current_account_id)
            self.roles = IAMRoles(client=self.client, current_account_id=current_account_id, region=region)

    def test_list_roles(self):
        self.assertTrue(self.roles.resources[0].name == "test-resource-exposure")
        self.assertTrue(self.roles.resources[0].arn == "arn:aws:iam::123456789012:role/test-resource-exposure")

    def test_get_rbp(self):
        expected_result = constants.EC2_ASSUME_ROLE_POLICY
        print(self.example.policy_document.original_policy)
        print(self.example.policy_document.original_policy)
        self.assertDictEqual(self.example.policy_document.original_policy, expected_result)
        print(self.example.policy_document)

    def test_set_rbp(self):
        after = self.example.set_rbp(constants.EC2_ASSUME_ROLE_POLICY)
        self.assertDictEqual(constants.EC2_ASSUME_ROLE_POLICY, after.updated_policy)

    def test_add_myself(self):
        result = self.example.add_myself(evil_principal=EVIL_PRINCIPAL)
        print(result.updated_policy_sids)
        self.assertListEqual(result.updated_policy_sids, ["", constants.ALLOW_CURRENT_ACCOUNT_SID_SIGNATURE, constants.SID_SIGNATURE])

    def tearDown(self):
        self.client.delete_role(RoleName=MY_RESOURCE)
        self.mock.stop()
