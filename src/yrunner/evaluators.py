import typing
import logging
import re

import requests

logger = logging.getLogger(__name__)

# secure builtins
# Allow some builtins, those that are safe
# This is used to evaluate expressions in "set"
BUILTINS = {
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


# Substitutes variables in a string
# Variables to be substituted are in the form {{ var }}
# Variables can be nested, e.g. {{ var1.var2 }}
# Use a regular expression to find all variables, and then substitute them
def eval_string(string: str, variables: typing.Mapping[str, typing.Any]) -> str:
    regex = re.compile(r"{{\s*([a-zA-Z0-9_]+(?:\.[a-zA-Z0-9_]+)*)\s*}}")
    for match in regex.finditer(string):
        var = match.group(1)
        value = variables
        for subvar in var.split('.'):
            value = value[subvar]
        string = string.replace(match.group(0), str(value))
    return string


def eval_expr(expr: str, variables: typing.Mapping[str, typing.Any]) -> typing.Any:
    return eval(expr, {"__builtins__": BUILTINS}, variables)  # nosec: Secure eval, only allow safe builtins (arithmetics, and a few more)

# Evaluate an expresion (used on "set") using "eval", without builtins (to avoid security issues)
def eval_set(data: typing.Mapping[str, str], variables: typing.MutableMapping[str, typing.Any]) -> typing.Any:
    if 'expr' in data:
        variables[data['var']] = eval_expr(data['expr'], variables)
    elif 'value' in data:
        variables[data['var']] = data['value']
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

    # Make request
    response = requests.request(**lrequest)

    # Store response
    if 'response_var' in request:
        variables[request['response_var']] = response

def eval_log(
    log: typing.Mapping[str, typing.Any], variables: typing.MutableMapping[str, typing.Any]
) -> None:
    # Convert to logging level
    level: int = logging.getLevelName(log.get('level', 'INFO').upper())

    logger.log(level, log['message'], *log['args'], **log['kwargs'])
