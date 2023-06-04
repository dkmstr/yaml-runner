import typing
import logging

from . import parsers
from . import evaluators

logger = logging.getLogger(__name__)


# To catch break on while loops
class LoopBreak(Exception):
    pass


# To catch continue on while loops
class LoopContinue(Exception):
    pass


# To catch exit
class Exit(Exception):
    def __init__(self, code: int) -> None:
        self.code = code


def exec_set(node: typing.Mapping[str, typing.Any], variables: typing.MutableMapping[str, typing.Any]) -> None:
    data = node['set']
    return evaluators.eval_set(node['set'], variables)


def exec_if(node: typing.Mapping[str, typing.Any], variables: typing.MutableMapping[str, typing.Any]) -> None:
    condition = evaluators.eval_expr(node['if']['condition'], variables)
    if condition:
        execute(node['if']['commands'], variables)


def exec_while(
    node: typing.Mapping[str, typing.Any], variables: typing.MutableMapping[str, typing.Any]
) -> None:
    while evaluators.eval_expr(node['while']['condition'], variables):
        try:
            execute(node['while']['commands'], variables)
        except LoopBreak:
            break
        except LoopContinue:
            continue


def exec_break(
    node: typing.Mapping[str, typing.Any], variables: typing.MutableMapping[str, typing.Any]
) -> None:
    raise LoopBreak()


def exec_continue(
    node: typing.Mapping[str, typing.Any], variables: typing.MutableMapping[str, typing.Any]
) -> None:
    raise LoopContinue()


def exec_exit(node: typing.Mapping[str, typing.Any], variables: typing.MutableMapping[str, typing.Any]) -> None:
    if 'code' in node['exit']:
        raise Exit(int(evaluators.eval_expr(node['exit']['code'], variables)))
    raise Exit(0)


def exec_request(
    node: typing.Mapping[str, typing.Any], variables: typing.MutableMapping[str, typing.Any]
) -> None:
    return evaluators.eval_request(node['request'], variables)


def exec_log(node: typing.Mapping[str, typing.Any], variables: typing.MutableMapping[str, typing.Any]) -> None:
    return evaluators.eval_log(node['log'], variables)


def exec_sleep(
    node: typing.Mapping[str, typing.Any], variables: typing.MutableMapping[str, typing.Any]
) -> None:
    return evaluators.eval_sleep(node['sleep'], variables)


executors: typing.Dict[
    str, typing.Callable[[typing.Mapping[str, typing.Any], typing.MutableMapping[str, typing.Any]], None]
] = {
    'set': exec_set,
    'if': exec_if,
    'while': exec_while,
    'break': exec_break,
    'continue': exec_continue,
    'exit': exec_exit,
    'request': exec_request,
    'log': exec_log,
    'sleep': exec_sleep,
}


def do_command(
    node: typing.Mapping[str, typing.Any], variables: typing.MutableMapping[str, typing.Any]
) -> None:
    # Node must have only one key
    if len(node) != 1:
        raise Exception(f"Invalid command: {node}")

    # Get command name
    command_name = list(node.keys())[0]

    # Execute command
    if command_name in executors:
        executors[command_name](node, variables)
    else:
        raise Exception(f"Invalid command: {node}")


def execute(
    commands: typing.List[typing.Mapping[str, typing.Any]], variables: typing.MutableMapping[str, typing.Any]
) -> None:
    # if commands is not an iterable, make it one
    if not isinstance(commands, typing.Iterable):
        commands = [commands]

    for command in commands:
        try:
            do_command(command, variables)
        except (Exit, LoopBreak, LoopContinue):
            raise
        except Exception as e:
            # Attach command to exception
            raise Exception(f"Error executing command: {command}") from e


# Interprets and executes the YAML file, return exit code
def run(script: str, variables: typing.MutableMapping[str, typing.Any]) -> int:
    # Parse YAML
    yaml = parsers.parse_yaml(script)

    # Execute
    try:
        execute(yaml, variables)
    except Exit as e:
        logger.info(f"Exit with code {e.code}")
        return e.code
    except LoopBreak:
        logger.error("Break outside of while loop")
        return -1
    except LoopContinue:
        logger.error("Continue outside of while loop")
        return -1
    except Exception as e:
        logger.error(f"Error: {e}")
        return -1

    return 0
