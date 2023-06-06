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


def exec_set(node: typing.Mapping[str, typing.Any], runner: 'YRunner') -> None:
    data = node['set']
    if 'value' in data:
        runner.set_variable(data['var'], runner.eval_expr(data['value']))
    else:
        raise exceptions.YRunnerInvalidParameter("Invalid set types.Command, missing 'value' parameter")


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


def exec_log(node: typing.Mapping[str, typing.Any], runner: 'YRunner') -> None:
    log = node['log']
    # Convert to logging level
    level: int = logging.getLevelName(log.get('level', 'INFO').upper())
    args = log.get('args', [])
    kwargs = log.get('kwargs', {})

    logger.log(level, runner.eval_string(log['message']), args, kwargs)


# Define internal commands
COMMANDS: typing.Final[typing.List[types.Command]] = [
    types.Command('set', exec_set, [types.CommandParameter('name'), types.CommandParameter('value')]),
    types.Command(
        'if', exec_if, [types.CommandParameter('condition'), types.CommandParameter('types.Commands')]
    ),
    types.Command(
        'while', exec_while, [types.CommandParameter('condition'), types.CommandParameter('types.Commands')]
    ),
    types.Command('break', exec_break),
    types.Command('continue', exec_continue),
    types.Command('exit', exec_exit, [types.CommandParameter('code', optional=True)]),
    types.Command('log', exec_log, [types.CommandParameter('message')]),
]
