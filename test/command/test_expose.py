import json
import unittest
from click.testing import CliRunner
from endgame.command.expose import expose


class ListResourcesClickUnitTests(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_expose_command_with_click(self):
        """command.expose.expose: should return exit code 0"""
        result = self.runner.invoke(expose, ["--help"])
        self.assertTrue(result.exit_code == 0)
