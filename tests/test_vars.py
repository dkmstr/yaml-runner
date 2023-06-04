from unittest import TestCase
import logging

from yrunner.runner import run

SETS_YAML = '''
- set:
    var: x0
    value: 5
- set:
    var: x1
    value: '"hello world"'  # escape the quotes, needed for YAML and our evaluator (it will be considered an expression otherwise)
- set:
    var: x2
    value: x1 * x0
'''

logger = logging.getLogger(__name__)


class TestVars(TestCase):
    def test_set(self):
        variables = {}
        result_code = run(SETS_YAML, variables)
        self.assertEqual(result_code, 0)
        self.assertEqual(variables['x0'], 5)
        self.assertEqual(variables['x1'], 'hello world')
        self.assertEqual(variables['x2'], 'hello worldhello worldhello worldhello worldhello world')

