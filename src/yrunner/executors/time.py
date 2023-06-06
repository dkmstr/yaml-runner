# Copyright (c) 2023 Adolfo Gómez García <dkmaster@dkmon.com>
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import typing
import time
import logging

from .. import exceptions, types

if typing.TYPE_CHECKING:
    from ..runner import YRunner

logger = logging.getLogger(__name__)


def exec_gettime(node: typing.Mapping[str, typing.Any], runner: 'YRunner') -> None:
    var = node['gettime']['var']
    runner.set_variable(var, time.time())


def exec_sleep(node: typing.Mapping[str, typing.Any], runner: 'YRunner') -> None:
    sleep = node['sleep']
    value = runner.eval_expr(sleep['value'])
    if isinstance(value, (int, float)):
        time.sleep(value)
    else:
        raise Exception("Invalid sleep types.Command")


# Define internal commands
COMMANDS: typing.Final[typing.List[types.Command]] = [
    types.Command('gettime', exec_gettime, [types.CommandParameter('var')]),
    types.Command('sleep', exec_sleep, [types.CommandParameter('seconds')]),
]
