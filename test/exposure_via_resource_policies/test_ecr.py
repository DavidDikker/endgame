import unittest
import warnings
from moto import mock_ecr
from endgame.exposure_via_resource_policies.ecr import EcrRepositories
from endgame.shared.aws_login import get_boto3_client

MY_RESOURCE = "test-resource-exposure"
EVIL_PRINCIPAL = "arn:aws:iam::999988887777:user/evil"


# https://github.com/spulec/moto/tree/master/tests/test_ecr
class EcrTestCase(unittest.TestCase):
    def setUp(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            self.mock = mock_ecr()
            self.mock.start()
            self.client = get_boto3_client(profile=None, service="ecr", region="us-east-1", cloak=False)
            self.client.create_repository(repositoryName=MY_RESOURCE)
            # get_resource_policy has not been implemented by moto for ecr
            # self.example = EcrRepository(name=MY_RESOURCE, region="us-east-1", client=self.client,
            #                              current_account_id="111122223333")
            self.repositories = EcrRepositories(client=self.client, current_account_id="111122223333", region="us-east-1")

    def test_list_resources(self):
        print()
        resource_names = []
        for resource in self.repositories.resources:
            resource_names.append(resource.name)
            print(resource.name)
        self.assertTrue("test-resource-exposure" in resource_names)

    # get_resource_policy has not been implemented by moto for ecr
    # def test_get_rbp(self):

    # put_resource_policy has not been implemented by moto for ecr
    # def test_set_rbp(self):
    # def test_add_myself(self):

    def tearDown(self):
        self.client.create_repository(repositoryName=MY_RESOURCE)
        self.mock.stop()
