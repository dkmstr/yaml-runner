from unittest import TestCase
import logging

from yrunner.runner import run

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
        variables = {}
        result_code = run(EXIT_YAML, variables)
        self.assertEqual(result_code, 32)
        self.assertEqual(variables['x0'], 5)

    def test_exit_expr(self):
        variables = {}
        result_code = run(EXIT_EXPR_YAML, variables)
        self.assertEqual(result_code, 10)
        self.assertEqual(variables['x0'], 5)

