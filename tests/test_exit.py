from unittest import TestCase
import logging

from yrunner import YRunner

EXIT_YAML = '''
- set:
    var: x0
    value: 5
- exit:
    code: 32
'''

EXIT_EXPR_YAML = '''
- set:
    var: x0
    value: 5
- exit:
    code: x0 * 2
'''


logger = logging.getLogger(__name__)


class TestExit(TestCase):
    def test_exit_code(self):
        runner = YRunner()
        result_code = runner.run(EXIT_YAML)
        self.assertEqual(result_code, 32)
        self.assertEqual(runner.variables['x0'], 5)

    def test_exit_expr(self):
        runner = YRunner()
        result_code = runner.run(EXIT_EXPR_YAML)
        self.assertEqual(result_code, 10)
        self.assertEqual(runner.variables['x0'], 5)

