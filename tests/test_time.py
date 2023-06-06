from unittest import TestCase
import time
import logging

from yrunner import YRunner
from yrunner.executors import time as ex_time

SLEEP_YAML = '''
---
- set:
    var: x0
    value: 5
- sleep:
    value: 0.4
'''

SLEEP_EXPR_YAML = '''
---
- set:
    var: x0
    value: 0.2
- sleep:
    value: x0 * 2
'''

GETTIME_YAML = '''
---
- gettime:
    var: x0
- sleep:
    value: 0.5
- gettime:
    var: x1
- set:
    var: x2
    value: x1 - x0
'''

logger = logging.getLogger(__name__)


class TestSleep(TestCase):
    def test_sleep_value(self):
        runner = YRunner(ex_time.COMMANDS)
        start_time = time.time()
        result_code = runner.run(SLEEP_YAML)
        end_time = time.time()
        self.assertTrue(end_time - start_time >= 0.4)
        self.assertEqual(result_code, 0)
        self.assertEqual(runner.variables['x0'], 5)

    def test_sleep_expr(self):
        runner = YRunner(ex_time.COMMANDS)
        start_time = time.time()
        result_code = runner.run(SLEEP_EXPR_YAML)
        end_time = time.time()
        self.assertTrue(end_time - start_time >= 0.4)
        self.assertEqual(result_code, 0)
        self.assertEqual(runner.variables['x0'], 0.2)

    def test_gettime(self):
        runner = YRunner(ex_time.COMMANDS)
        result_code = runner.run(GETTIME_YAML)
        self.assertEqual(result_code, 0)
        self.assertTrue(runner.variables['x2'] >= 0.5)