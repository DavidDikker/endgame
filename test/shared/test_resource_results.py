import unittest
import warnings
from moto import mock_kms, mock_iam, mock_ecr
from endgame.shared.aws_login import get_boto3_client
import json
from endgame.shared import constants, utils
from endgame.shared.resource_results import ResourceResults, ServiceResourcesMultiRegion, ServiceResourcesSingleRegion


class ResourceResultsTestCase(unittest.TestCase):
    def setUp(self):
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            self.mock_kms = mock_kms()
            self.mock_iam = mock_iam()
            self.mock_ecr = mock_ecr()
            self.mock_kms.start()
            self.mock_ecr.start()
            self.mock_iam.start()
            self.current_account_id = "123456789012"
            # Set up KMS keys in 3 regions
            self.ue1_kms_client = get_boto3_client(profile=None, service="kms", region="us-east-1")
            self.ue2_kms_client = get_boto3_client(profile=None, service="kms", region="us-east-2")
            self.euw1_kms_client = get_boto3_client(profile=None, service="kms", region="eu-west-1")
            region = "us-east-1"
            self.iam_client = get_boto3_client(profile=None, service="iam", region=region)

            # self.iam_client = get_boto3_client(profile=None, service="iam", region="us-east-1")
            self.uw1_ecr_client = get_boto3_client(profile=None, service="ecr", region="us-west-1")

            # Get the ARNs so you can test them later
            self.ue1_key_arn = self.ue1_kms_client.create_key()["KeyMetadata"]["Arn"]
            self.ue2_key_arn = self.ue2_kms_client.create_key()["KeyMetadata"]["Arn"]
            self.euw1_key_arn = self.euw1_kms_client.create_key()["KeyMetadata"]["Arn"]
            iam_role = self.iam_client.create_role(
                RoleName="yolo",
                AssumeRolePolicyDocument=json.dumps(constants.EC2_ASSUME_ROLE_POLICY)
            )
            self.iam_role_arn = iam_role["Role"]["Arn"]
            self.ecr_arn = self.uw1_ecr_client.create_repository(repositoryName="alpine")["repository"]["repositoryArn"]

            # Create the objects that will store our results
            self.service_resources_single_region = ServiceResourcesSingleRegion(
                user_provided_service="kms",
                region="us-east-1",
                current_account_id=self.current_account_id,
                profile=None,
                cloak=False
            )
            self.service_resources_multi_region = ServiceResourcesMultiRegion(
                user_provided_service="kms",
                user_provided_region="all",
                current_account_id=self.current_account_id,
                profile=None,
                cloak=False
            )
            # Let's exclude all the services that do not match the ones we specified above.
            # That way, we can avoid an issue where moto tries to make API calls it does not support
            excluded_services = []
            for supported_service in constants.SUPPORTED_AWS_SERVICES:
                if supported_service not in ["all", "iam", "ecr", "kms"]:
                    excluded_services.append(supported_service)
            print(f"Excluded services: {excluded_services}")
            self.resource_results = ResourceResults(
                user_provided_service="all",
                user_provided_region="all",
                current_account_id=self.current_account_id,
                profile=None,
                cloak=False,
                excluded_names=[],
                excluded_services=excluded_services
            )

    def test_kms_single_region_arns(self):
        results = self.service_resources_single_region.resources
        for resource in results.resources:
            print(resource.arn)

        expected_results = [self.ue1_key_arn]
        print(self.service_resources_single_region.arns)
        self.assertListEqual(self.service_resources_single_region.arns, expected_results)

    def test_kms_regions_multi_regions(self):
        print("Test which regions the service appears in")
        expected_regions = ['af-south-1', 'ap-east-1', 'ap-northeast-1', 'ap-northeast-2', 'ap-south-1',
                            'ap-southeast-1', 'ap-southeast-2', 'ca-central-1', 'eu-central-1', 'eu-north-1',
                            'eu-south-1', 'eu-west-1', 'eu-west-2', 'eu-west-3', 'me-south-1', 'sa-east-1', 'us-east-1',
                            'us-east-2', 'us-west-1', 'us-west-2']
        kms_regions = self.service_resources_multi_region.regions
        print(kms_regions)
        # Let's future proof the tests, which is important once AWS adds more regions
        for kms_region in kms_regions:
            self.assertTrue(kms_region in expected_regions)

    def test_kms_arns_multi_regions(self):
        print("Test resource ARNs")
        arns = self.service_resources_multi_region.arns
        expected_arns = [
            self.ue1_key_arn,
            self.ue2_key_arn,
            self.euw1_key_arn
        ]
        print(arns)
        for arn in expected_arns:
            self.assertTrue(arn in arns)

    def test_resource_results_arns(self):
        print("Get ARNs from all the different services")
        arns = self.resource_results.arns()
        print(arns)
        expected_arns = [
            self.ue1_key_arn,
            self.ue2_key_arn,
            self.euw1_key_arn,
            self.iam_role_arn,
            self.ecr_arn
        ]
        for arn in expected_arns:
            self.assertTrue(arn in arns)
