import json
import unittest
from click.testing import CliRunner
from endgame.command.list_resources import list_resources


class ListResourcesClickUnitTests(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_list_resources_command_with_click(self):
        """command.list_resources.list_resources: should return exit code 0"""
        result = self.runner.invoke(list_resources, ["--help"])
        self.assertTrue(result.exit_code == 0)

        result = self.runner.invoke(list_resources, ["--service", "s3", "-v"])
        print(result)
