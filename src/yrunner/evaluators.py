import typing
import logging
import time
import re

import requests

logger = logging.getLogger(__name__)

# secure builtins
# Allow some builtins, those that are safe
# This is used to evaluate expressions in "set"
BUILTINS: typing.Final[typing.Dict[str, typing.Callable]] = {
    'abs': abs,
    'all': all,
    'any': any,
    'bool': bool,
    'str': str,
    'int': int,
    'float': float,
    'len': len,
    'max': max,
    'min': min,
    'round': round,
    'sum': sum,
}
# regex to find variables in a string
INTERPOLATE_REGEX: typing.Final[re.Pattern] = re.compile(r'{{\s*(.*?)\s*}}')


# Substitutes (evaluates) variables in a string
# Variables to be substituted are in the form {{ expression }} (or expressions {{ var + 1 }})
def eval_string(string: str, variables: typing.Mapping[str, typing.Any]) -> str:
    for match in INTERPOLATE_REGEX.finditer(string):
        value = eval_expr(match.group(1), variables)  # evaluate the expressio
        string = string.replace(match.group(0), str(value))
    return string


def eval_expr(
    expr: str,
    variables: typing.Mapping[str, typing.Any],
    *,
    force_quotes: bool = False,  # Force quotes on strings
) -> typing.Any:
    if isinstance(expr, str):
        if force_quotes:
            expr = '"' + expr + '"'
        ret = eval(
            expr, {"__builtins__": BUILTINS}, variables
        )  # nosec: Secure eval, only allow safe builtins (arithmetics, and a few more)
    else:
        ret = expr
    return ret


# Evaluate an expresion (used on "set") using "eval", without builtins (to avoid security issues)
def eval_set(data: typing.Mapping[str, str], variables: typing.MutableMapping[str, typing.Any]) -> typing.Any:
    if 'value' in data:
        variables[data['var']] = eval_expr(data['value'], variables)
    else:
        raise Exception("Invalid set command")


# Evaluates (and makes) an HTTP request
def eval_request(
    request: typing.Mapping[str, typing.Any], variables: typing.MutableMapping[str, typing.Any]
) -> None:
    # Make a copy of the request, removing non-requests parameters
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
    lrequest['url'] = eval_string(lrequest['url'], variables)
    # If parameters are present,
    if 'params' in lrequest:
        if isinstance(lrequest['params'], str):
            lrequest['params'] = eval_string(lrequest['params'], variables)
        elif isinstance(lrequest['params'], dict):
            lrequest['params'] = {k: eval_string(v, variables) for k, v in lrequest['params'].items()}

    # Make request
    response = requests.request(**lrequest)

    # Store response
    if 'response_var' in request:
        variables[request['response_var']] = response


def eval_log(log: typing.Mapping[str, typing.Any], variables: typing.MutableMapping[str, typing.Any]) -> None:
    # Convert to logging level
    level: int = logging.getLevelName(log.get('level', 'INFO').upper())
    args = log.get('args', [])
    kwargs = log.get('kwargs', {})

    logger.log(level, eval_string(log['message'], variables), args, kwargs)


def eval_sleep(
    sleep: typing.Mapping[str, typing.Any], variables: typing.MutableMapping[str, typing.Any]
) -> None:
    value = eval_expr(sleep['value'], variables)
    if isinstance(value, (int, float)):
        time.sleep(value)
    else:
        raise Exception("Invalid sleep command")
