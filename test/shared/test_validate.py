import json
import unittest
from click.testing import CliRunner
import datetime
from endgame.shared.validate import validate_user_or_principal_arn, click_validate_comma_separated_resource_names


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

    def test_click_validate_comma_separated_resource_names(self):
        """shared.validate.click_validate_comma_separated_resource_names: Should return values properly"""
        self.assertIsNone(click_validate_comma_separated_resource_names(ctx=None, param=None, value=None))
        self.assertIsInstance(click_validate_comma_separated_resource_names(ctx=None, param=None, value=""), list)
        self.assertListEqual(click_validate_comma_separated_resource_names(ctx=None, param=None, value=""), [])
        comma_separated_string = "victimbucket1,victimbucket2,victimbucket3"
        result = click_validate_comma_separated_resource_names(ctx=None, param=None, value=comma_separated_string)
        expected_result = ['victimbucket1', 'victimbucket2', 'victimbucket3']
        self.assertListEqual(result, expected_result)
        with self.assertRaises(Exception):
            click_validate_comma_separated_resource_names(ctx=None, param=None, value={})

