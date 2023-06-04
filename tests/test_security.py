from unittest import TestCase
import logging

from yrunner import YRunner
from yrunner import exceptions

INTERNALS_YAML = '''
- set:
    var: x0
    value: max.__import__('os').system('echo hello world')
- exit:
    code: x0 * 2
'''


logger = logging.getLogger(__name__)


class TestExit(TestCase):
    def test_no_internals(self):
        runner = YRunner()
        result_code = runner.run(INTERNALS_YAML)
        self.assertEqual(result_code, -1)
        self.assertNotIn('x0', runner.variables)
        self.assertIsInstance(runner.error, exceptions.YRunnerInvalidContent)
    