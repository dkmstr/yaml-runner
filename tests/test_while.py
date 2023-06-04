from unittest import TestCase
import logging

from yrunner import YRunner

WHILE_YAML = '''
---
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

WHILE_BREAK_YAML = '''
---
- set:
    var: x0
    value: 5
- while:
    condition: x0 > 0
    commands:
        - set:
            var: x0
            value: x0 - 1
        - if:
            condition: x0 == 2
            commands:
                - break
'''

logger = logging.getLogger(__name__)


class TestWhile(TestCase):
    def test_while(self):
        runner = YRunner()
        result_code = runner.run(WHILE_YAML)
        self.assertEqual(result_code, 0)
        self.assertEqual(runner.variables['x0'], 0)

    def test_while_break(self):
        runner = YRunner()
        result_code = runner.run(WHILE_BREAK_YAML)
        self.assertEqual(result_code, 0)
        self.assertEqual(runner.variables['x0'], 2)
