import json
import os
import unittest
import warnings
from moto import mock_s3, mock_sts
from click.testing import CliRunner
from endgame.command.list_resources import list_resources
from endgame.shared.aws_login import get_boto3_client, get_current_account_id


class ListResourcesClickUnitTests(unittest.TestCase):
    """Test listing S3 resources using the CLI"""

    def setUp(self):
        self.runner = CliRunner()
        # Set up mocked boto3 resources
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            region = "us-east-1"
            current_account_id = "123456789012"
            bucket_names = [
                "victimbucket1",
                "victimbucket2",
                "victimbucket3",
            ]
            self.mock = mock_s3()
            self.mock.start()
            self.mock_sts = mock_sts()
            self.mock_sts.start()
            self.client = get_boto3_client(profile=None, service="s3", region=region)
            self.sts_client = get_boto3_client(profile=None, service="sts", region=region)
            for bucket in bucket_names:
                self.client.create_bucket(Bucket=bucket)
            # response = self.client.list_buckets()

    def test_list_resources_command_with_click(self):
        """command.list_resources.list_resources: Print out mocked AWS S3 resources properly"""
        result = self.runner.invoke(list_resources, ["--help"])
        self.assertTrue(result.exit_code == 0)

        result = self.runner.invoke(list_resources, ["--service", "s3", "-v"])
        expected_output = "victimbucket1\nvictimbucket2\nvictimbucket3\n"
        print(result.output)
        self.assertTrue(result.exit_code == 0)
        self.assertEqual(result.output, expected_output)

    def test_list_resources_exclusion_via_argument(self):
        """command.list_resources.list_resources: Exclude resources using argument"""
        result = self.runner.invoke(list_resources, ["--service", "s3", "--exclude", "victimbucket2"])
        print(result.output)
        self.assertEqual(result.output, "victimbucket1\nvictimbucket3\n")

    def test_list_resources_exclusion_via_envvar(self):
        """command.list_resources.list_resources: Exclude resources using environment variable"""
        os.environ["EXCLUDED_NAMES"] = "victimbucket1"
        result = self.runner.invoke(list_resources, ["--service", "s3"])
        print(result.output)
        self.assertEqual(result.output, "victimbucket2\nvictimbucket3\n")

    def test_list_resources_exclude_multiple(self):
        result = self.runner.invoke(list_resources, ["--service", "s3", "--exclude", "victimbucket1,victimbucket2"])
        print(result.output)
        self.assertEqual(result.output, "victimbucket3\n")
