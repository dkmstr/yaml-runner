from unittest import TestCase
import logging

from yrunner.runner import run

WHILE_YAML = '''
- set:
    var: x0
    value: 5
- while:
    condition: x0 > 0
    commands:
        - set:
            var: x0
            value: x0 - 1
'''

logger = logging.getLogger(__name__)


class TestIf(TestCase):
    def test_while(self):
        variables = {}
        result_code = run(WHILE_YAML, variables)
        self.assertEqual(result_code, 0)
        self.assertEqual(variables['x0'], 0)
