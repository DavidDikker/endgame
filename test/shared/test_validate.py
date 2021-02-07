import json
import unittest
from click.testing import CliRunner
import datetime
from endgame.shared.validate import validate_user_or_principal_arn


class ValidateTestCase(unittest.TestCase):

    def test_validate_user_or_principal_arn(self):
        """shared.validate.validate_user_or_principal_arn: should highlight user ARNs properly"""
        user_arn = "arn:aws:iam::123456789012:user/kmcquade"
        role_arn = "arn:aws:iam::123456789012:role/myrole"

        invalid_arn_1 = "arn:aws:iam::123456789012:sup/notreal"
        invalid_arn_2 = "arn:aws:s3:::test-bucket"
        self.assertTrue(validate_user_or_principal_arn(user_arn))
        self.assertTrue(validate_user_or_principal_arn(role_arn))
        with self.assertRaises(Exception):
            validate_user_or_principal_arn(invalid_arn_1)
        with self.assertRaises(Exception):
            validate_user_or_principal_arn(invalid_arn_2)
