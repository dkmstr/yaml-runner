import typing
import logging

import requests

from .. import types

if typing.TYPE_CHECKING:
    from ..runner import YRunner

logger = logging.getLogger(__name__)


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

# Define internal commands
COMMANDS: typing.Final[typing.List[types.Command]] = [
    types.Command(
        'request',
        exec_request,
        [
            types.CommandParameter('method'),
            types.CommandParameter('url'),
            types.CommandParameter('params', True),
            types.CommandParameter('data', True),
            types.CommandParameter('headers', True),
            types.CommandParameter('cookies', True),
            types.CommandParameter('auth', True),
            types.CommandParameter('timeout', True),
            types.CommandParameter('allow_redirects', True),
            types.CommandParameter('proxies', True),
            types.CommandParameter('hooks', True),
            types.CommandParameter('stream', True),
            types.CommandParameter('verify', True),
            types.CommandParameter('cert', True),
        ],
    ),
]
