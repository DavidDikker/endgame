import os
import json
import unittest
import warnings
from moto import mock_s3, mock_sts
from click.testing import CliRunner
from endgame.shared.aws_login import get_boto3_client, get_current_account_id
from endgame.command.list_resources import list_resources
from endgame.command.smash import smash
EVIL_PRINCIPAL = "arn:aws:iam::999988887777:user/evil"

BUCKET_NAMES = [
    "victimbucket1",
    "victimbucket2",
    "victimbucket3",
]


class SmashClickUnitTests(unittest.TestCase):
    """Test listing S3 resources using the CLI"""

    def setUp(self):
        self.runner = CliRunner()
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            region = "us-east-1"
            self.mock = mock_s3()
            self.mock.start()
            self.mock_sts = mock_sts()
            self.mock_sts.start()
            self.client = get_boto3_client(profile=None, service="s3", region=region)
            for bucket in BUCKET_NAMES:
                self.client.create_bucket(Bucket=bucket)
            os.environ["EVIL_PRINCIPAL"] = EVIL_PRINCIPAL

    def test_smash_help(self):
        """command.smash.smash: Print help"""
        result = self.runner.invoke(smash, ["--help"])
        self.assertTrue(result.exit_code == 0)

    def test_smash_dry_run(self):
        """command.smash.smash: Dry run"""
        smash_result = self.runner.invoke(smash, ["--service", "s3", "--dry-run"])
        print(smash_result.output)
        self.assertTrue(smash_result.exit_code == 0)

    def tearDown(self):
        for bucket in BUCKET_NAMES:
            self.client.delete_bucket(Bucket=bucket)
        self.mock.stop()


class SmashClickUnitTestsWithExclusions(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            region = "us-east-1"
            self.mock = mock_s3()
            self.mock.start()
            self.mock_sts = mock_sts()
            self.mock_sts.start()
            self.client = get_boto3_client(profile=None, service="s3", region=region)
            for bucket in BUCKET_NAMES:
                self.client.create_bucket(Bucket=bucket)
            os.environ["EVIL_PRINCIPAL"] = EVIL_PRINCIPAL

    def test_smash_live_run(self):
        """command.smash.smash: Live run"""
        os.environ["EXCLUDED_NAMES"] = "victimbucket1"
        smash_result = self.runner.invoke(smash, ["--service", "s3"])
        self.assertTrue(smash_result.exit_code == 0)
        print(smash_result.output)
        count = smash_result.output.count("SUCCESS")
        self.assertEqual(count, 2)

    def tearDown(self):
        for bucket in BUCKET_NAMES:
            self.client.delete_bucket(Bucket=bucket)
        self.mock.stop()
