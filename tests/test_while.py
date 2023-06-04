from unittest import TestCase
import logging

from yrunner import YRunner

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
        runner = YRunner()
        result_code = runner.run(WHILE_YAML)
        self.assertEqual(result_code, 0)
        self.assertEqual(runner.variables['x0'], 0)
