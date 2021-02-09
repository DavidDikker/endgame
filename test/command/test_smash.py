import json
import unittest
from tabulate import tabulate
from click.testing import CliRunner
from endgame.command.expose import expose
from endgame.shared import utils
#
#
# class SmashTabulateFormat(unittest.TestCase):
#     def setUp(self):
#         self.headers = ["Operation", "", "Resource"]
#         self.data = [
#             [f"", "arn:aws:sns:us-east-2:111122223333:test-resource-exposure"],
#             ["arn:aws:iam::999988887777:user/evil", "arn:aws:s3:::fakebucket"],
#             ["arn:aws:iam::999988887777:user/evil", "arn:aws:iam::111122223333:test-role"]
#         ]
#
#     def test_tabulate(self):
#         """test tabulate printing plain"""
#         print(tabulate(self.data, self.headers, tablefmt="plain"))
#
#     def test_tabulate_other_formats(self):
#         print(tabulate(self.data, self.headers, tablefmt="simple"))
