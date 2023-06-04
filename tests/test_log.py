from unittest import TestCase, mock
import logging

from yrunner.runner import run
from yrunner import evaluators

IF_YAML = '''
- set:
    var: x0
    value: 5
- log:
    level: warning
    message: "x0 is {{ x0 }}"
'''

logger = logging.getLogger(__name__)


class Testlog(TestCase):
    def test_log(self):
        # patch the logger of evaluators
        with mock.patch.object(evaluators, 'logger') as mock_logger:
            variables = {}
            result_code = run(IF_YAML, variables)
            self.assertEqual(result_code, 0)
            self.assertEqual(variables['x0'], 5)
            mock_logger.log.assert_called_once_with(logging.WARNING, 'x0 is 5', [], {})
