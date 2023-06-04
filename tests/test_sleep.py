from unittest import TestCase
import time
import logging

from yrunner.runner import run

SLEEP_YAML = '''
---
- set:
    var: x0
    value: 5
- sleep:
    value: 1   
'''

SLEEP_EXPR_YAML = '''
---
- set:
    var: x0
    value: 0.6
- sleep:
    value: x0 * 2
'''

logger = logging.getLogger(__name__)


class TestSleep(TestCase):
    def test_sleep_value(self):
        variables = {}
        start_time = time.time()
        result_code = run(SLEEP_YAML, variables)
        end_time = time.time()
        self.assertTrue(end_time - start_time >= 1)
        self.assertEqual(result_code, 0)
        self.assertEqual(variables['x0'], 5)

    def test_sleep_expr(self):
        variables = {}
        start_time = time.time()
        result_code = run(SLEEP_EXPR_YAML, variables)
        end_time = time.time()
        self.assertTrue(end_time - start_time >= 1.2)
        self.assertEqual(result_code, 0)
        self.assertEqual(variables['x0'], 0.6)