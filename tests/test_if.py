from unittest import TestCase
import logging

from yrunner.runner import run

IF_YAML = '''
- set:
    var: x0
    value: 5
- if:
    condition: x0 == 5
    commands:
        - set:
            var: x1
            value: '"hello world"'
- if:
    condition: x0 == 10
    commands:
        - set:
            var: x1
            value: '"NO hello world"'
'''

logger = logging.getLogger(__name__)


class TestIf(TestCase):
    def test_if(self):
        variables = {}
        result_code = run(IF_YAML, variables)
        self.assertEqual(result_code, 0)
        self.assertEqual(variables['x0'], 5)
        self.assertEqual(variables['x1'], 'hello world')
