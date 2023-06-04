import typing
import time
import logging

import requests

from . import exceptions

if typing.TYPE_CHECKING:
    from .runner import YRunner

logger = logging.getLogger(__name__)


def exec_set(node: typing.Mapping[str, typing.Any], runner: 'YRunner') -> None:
    data = node['set']
    if 'value' in data:
        runner.set_variable(data['var'], runner.eval_expr(data['value']))
    else:
        raise exceptions.YRunnerInvalidParameter("Invalid set command, missing 'value' parameter")


def exec_if(node: typing.Mapping[str, typing.Any], runner: 'YRunner') -> None:
    condition = runner.eval_expr(node['if']['condition'])
    if condition:
        runner.execute(node['if']['commands'])


def exec_while(node: typing.Mapping[str, typing.Any], runner: 'YRunner') -> None:
    while runner.eval_expr(node['while']['condition']):
        try:
            runner.execute(node['while']['commands'])
        except exceptions.LoopBreak:
            break
        except exceptions.LoopContinue:
            continue


def exec_break(node: typing.Mapping[str, typing.Any], runner: 'YRunner') -> None:
    raise exceptions.LoopBreak()


def exec_continue(node: typing.Mapping[str, typing.Any], runner: 'YRunner') -> None:
    raise exceptions.LoopContinue()


def exec_exit(node: typing.Mapping[str, typing.Any], runner: 'YRunner') -> None:
    if 'code' in node['exit']:
        raise exceptions.Exit(int(runner.eval_expr(node['exit']['code'])))
    raise exceptions.Exit(0)


def exec_request(node: typing.Mapping[str, typing.Any], runner: 'YRunner') -> None:
    # Make a copy of the request, removing non-requests parameters
    request = node['request']
    lrequest = {
        k: v
        for k, v in request.items()
        if k
        in [
            'method',
            'url',
            'params',
            'data',
            'headers',
            'cookies',
            'auth',
            'timeout',
            'allow_redirects',
            'proxies',
            'hooks',
            'stream',
            'verify',
            'cert',
        ]
    }

    # Fix url with eval_string
    lrequest['url'] = runner.eval_string(lrequest['url'])
    # If parameters are present,
    if 'params' in lrequest:
        if isinstance(lrequest['params'], str):
            lrequest['params'] = runner.eval_string(lrequest['params'])
        elif isinstance(lrequest['params'], dict):
            lrequest['params'] = {k: runner.eval_string(v) for k, v in lrequest['params'].items()}

    # Make request
    response = requests.request(**lrequest)

    # Store response
    if 'response_var' in request:
        runner.set_variable(request['response_var'], response)


def exec_log(node: typing.Mapping[str, typing.Any], runner: 'YRunner') -> None:
    log = node['log']
    # Convert to logging level
    level: int = logging.getLevelName(log.get('level', 'INFO').upper())
    args = log.get('args', [])
    kwargs = log.get('kwargs', {})

    logger.log(level, runner.eval_string(log['message']), args, kwargs)


def exec_sleep(node: typing.Mapping[str, typing.Any], runner: 'YRunner') -> None:
    sleep = node['sleep']
    value = runner.eval_expr(sleep['value'])
    if isinstance(value, (int, float)):
        time.sleep(value)
    else:
        raise Exception("Invalid sleep command")
