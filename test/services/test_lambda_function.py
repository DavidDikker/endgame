# import os
# import unittest
# import warnings
# import json
# import io
# import zipfile
# from moto import mock_lambda, mock_iam
# from moto.awslambda import lambda_backends
# import boto3
# from policy_sentry.util.policy_files import get_sid_names_from_policy
# from endgame.services.lambda_function import LambdaFunction
# from endgame.shared.aws_login import get_boto3_client
# from endgame.shared import constants
#
# MY_RESOURCE = "lambda-test-resource-exposure"
# EVIL_PRINCIPAL = "arn:aws:iam::999988887777:user/evil"
# LAMBDA_ZIP_PATH = os.path.abspath(
#     os.path.join(os.path.pardir, os.path.pardir, "terraform", "lambda-function", "lambda.zip"))
# AWS_FAKE_ENDPOINT = 'http://moto:5000'
#
#
# # Taken from moto unit tests: https://github.com/spulec/moto/blob/d382731a14784cced93ed1a180d3905461825ef2/tests/test_awslambda/test_lambda.py#L35
# # Taken from moto issues: https://github.com/spulec/moto/issues/3150
# def _process_lambda(func_str):
#     zip_bytes_io = io.BytesIO()
#     with zipfile.ZipFile(zip_bytes_io, 'w', zipfile.ZIP_DEFLATED) as f:
#         f.writestr('lambda_function.py', func_str)
#     zip_bytes_io.seek(0)
#     return zip_bytes_io.read()
#
#
# LAMBDA_NAME = 'lambda_name'
# func_str = """
# def lambda_handler(event, context):
#     print("custom log event")
#     return event
# """
# iam_client = boto3.client('iam', region_name='us-east-1',
#                           endpoint_url=AWS_FAKE_ENDPOINT)
#
# lambda_client = boto3.client('lambda', region_name='us-east-1',
#                              endpoint_url=AWS_FAKE_ENDPOINT)
#
#
# class LambdaTestCase(unittest.TestCase):
#     def setUp(self):
#         with warnings.catch_warnings():
#             warnings.filterwarnings("ignore", category=DeprecationWarning)
#             # Create an IAM role - that is a prerequisite for Lambda function
#             self.iam_mock = mock_iam()
#             self.iam_client = boto3.client('iam', region_name='us-east-1',
#                                       endpoint_url=AWS_FAKE_ENDPOINT)
#             # self.iam_client = get_boto3_client(profile=None, service="iam", region="us-east-1")
#             # self.iam_client.create_role(RoleName=MY_RESOURCE, AssumeRolePolicyDocument=json.dumps(constants.EC2_ASSUME_ROLE_POLICY))
#
#             self.mock = mock_lambda()
#             self.mock.start()
#             self.client = boto3.client('lambda', region_name='us-east-1',
#                                          endpoint_url=AWS_FAKE_ENDPOINT)
#             # self.client = get_boto3_client(profile=None, service="lambda", region="us-east-1")
#
#             self.client.create_function(
#                 FunctionName=MY_RESOURCE,
#                 Runtime="python3.8",
#                 Role=MY_RESOURCE,
#                 Handler='lambda_function.lambda_handler',
#                 Description="test lambda function",
#                 PackageType="Zip",
#                 Code={"ZipFile": _process_lambda(func_str)},
#                 # Code={"ZipFile": open(LAMBDA_ZIP_PATH, 'rb').read()},
#                 Timeout=3,
#                 MemorySize=128,
#                 Publish=True,
#             )
#             self.example = LambdaFunction(name=MY_RESOURCE, region="us-east-1", client=self.client,
#                                           current_account_id="111122223333")
#
#     def test_get_rbp(self):
#         expected_result = {'Version': '2012-10-17', 'Statement': []}
#         self.assertDictEqual(self.example.original_policy, expected_result)
#
#     def test_set_rbp(self):
#         before = {
#             'Version': '2012-10-17',
#             'Statement': [
#                 {
#                     "Sid": "Yolo",
#                     "Effect": "Allow",
#                     "Principal": {"AWS": [f"arn:aws:iam::999988887777:user/canttouchthis"]},
#                     "Action": "*:*",
#                     "Resource": "*:*",
#                 }
#             ]
#         }
#         after = self.example.set_rbp(before)
#         self.assertDictEqual(before, after)
#
#     def test_add_myself(self):
#         result = self.example.add_myself(evil_principal=EVIL_PRINCIPAL)
#         sids = get_sid_names_from_policy(result)
#         print(sids)
#         self.assertListEqual(sids, [constants.ALLOW_CURRENT_ACCOUNT_SID_SIGNATURE, f"{constants.SID_SIGNATURE}"])
#
#     def tearDown(self):
#         self.client.delete_bucket(Bucket=MY_RESOURCE)
#         self.mock.stop()
