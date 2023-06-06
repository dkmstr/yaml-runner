import typing
import logging
from unittest import TestCase

from yrunner import YRunner

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
- set:
    var: x3
    value: passed_in * 2  # passed_in is a variable passed in from the command line
- set:
    var: x4
    value: "lambda x: x * 2"  # Need quotes to escape the ":", otherwise YAML will think it's a dictionary
- set:
    var: x5
    value: x4(x0)
'''

logger = logging.getLogger(__name__)


class TestVars(TestCase):
    def test_set(self) -> None:
        variables: typing.Dict[str, typing.Any] = {'passed_in': 'hello world'}
        runner = YRunner(variables=variables)
        result_code = runner.run(SETS_YAML)
        self.assertEqual(result_code, 0)

        # Assert variables is same as runner.variables
        self.assertEqual(variables, runner.variables)

        # And now validate the variables
        self.assertEqual(variables['x0'], 5)
        self.assertEqual(variables['x1'], 'hello world')
        self.assertEqual(variables['x2'], 'hello worldhello worldhello worldhello worldhello world')
        self.assertEqual(variables['x3'], 'hello worldhello world')
        self.assertEqual(variables['x4'](5), 10)


