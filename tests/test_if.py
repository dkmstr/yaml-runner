from unittest import TestCase
import logging

from yrunner import YRunner

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
        runner = YRunner()
        result_code = runner.run(IF_YAML)
        self.assertEqual(result_code, 0)
        self.assertEqual(runner.variables['x0'], 5)
        self.assertEqual(runner.variables['x1'], 'hello world')
