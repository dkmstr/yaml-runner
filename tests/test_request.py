from unittest import TestCase

from yrunner import YRunner

REQUEST_YAML = '''
---
- set:
    var: x0
    value: 5
- request:
    url: "https://httpbin.org/get"  # must be an expression
    method: GET
    headers:
        Accept: application/json
    params:
        var: "{{x0}}"
'''

REQUEST_VAR_YAML = '''
---
- set:
    var: x0
    value: '"get"'
- request:
    url: "https://httpbin.org/{{x0}}"
    method: GET
    headers:
        Accept: application/json
    params: { var: "{{ x0 }}" }
    response_var: response
'''


class TestRequest(TestCase):
    def test_request(self):
        runner = YRunner()
        result_code = runner.run(REQUEST_YAML)
        self.assertEqual(result_code, 0)

    def test_request_var(self):
        runner = YRunner()
        result_code = runner.run(REQUEST_VAR_YAML)
        self.assertEqual(result_code, 0)
        self.assertEqual(runner.variables['response'].status_code, 200)
        self.assertEqual(runner.variables['response'].url, 'https://httpbin.org/get?var=get')
