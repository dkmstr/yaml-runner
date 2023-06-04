import typing
import re
import logging

from . import parsers
from . import exceptions
from . import internal_executors

logger = logging.getLogger(__name__)


class CommandParameter(typing.NamedTuple):
    name: str
    optional: bool = False
    default: typing.Any = None


class Command(typing.NamedTuple):
    name: str
    executor: typing.Callable[[typing.Mapping[str, typing.Any], 'YRunner'], None]
    parameters: typing.Optional[
        typing.List[CommandParameter]
    ] = []  # None means any parameter, empty list means no parameters


COMMANDS: typing.Final[typing.Dict[str, Command]] = {
    'set': Command('set', internal_executors.exec_set, [CommandParameter('name'), CommandParameter('value')]),
    'if': Command('if', internal_executors.exec_if, [CommandParameter('condition'), CommandParameter('commands')]),
    'while': Command('while', internal_executors.exec_while, [CommandParameter('condition'), CommandParameter('commands')]),
    'break': Command('break', internal_executors.exec_break),
    'continue': Command('continue', internal_executors.exec_continue),
    'exit': Command('exit', internal_executors.exec_exit, [CommandParameter('code', True)]),
    'log': Command('log', internal_executors.exec_log, [CommandParameter('message')]),
    'sleep': Command('sleep', internal_executors.exec_sleep, [CommandParameter('seconds')]),
    'request': Command(
        'request',
        internal_executors.exec_request,
        [
            CommandParameter('method'),
            CommandParameter('url'),
            CommandParameter('params', True),
            CommandParameter('data', True),
            CommandParameter('headers', True),
            CommandParameter('cookies', True),
            CommandParameter('auth', True),
            CommandParameter('timeout', True),
            CommandParameter('allow_redirects', True),
            CommandParameter('proxies', True),
            CommandParameter('hooks', True),
            CommandParameter('stream', True),
            CommandParameter('verify', True),
            CommandParameter('cert', True),
        ],
    ),
}


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


class YRunner:
    commands: typing.Dict[str, Command]
    variables: typing.MutableMapping[str, typing.Any]
    error: typing.Optional[Exception] = None

    def __init__(
        self,
        variables: typing.Optional[typing.MutableMapping[str, typing.Any]] = None,
        extra_commands: typing.Optional[typing.List[Command]] = None,
    ) -> None:
        # copy COMMANDS to self.commands
        self.commands = COMMANDS.copy()
        if extra_commands is not None:
            for command in extra_commands:
                self.commands[command.name] = command

        if variables is None:
            variables = {}
            
        self.variables = variables  # reference to the variables

    def _exec_command(self, node: typing.Mapping[str, typing.Any]) -> None:
        # Node must have only one key
        if len(node) != 1:
            raise Exception(f"Invalid command: {node}")

        # Get command name
        command_name = list(node.keys())[0]

        # Execute command
        cmd = self.commands.get(command_name)
        if cmd is None:
            raise exceptions.YRunnerInvalidCommand(f"Invalid command: {node}")
        cmd.executor(node, self)

    def execute(self, commands: typing.List[typing.Mapping[str, typing.Any]]) -> None:
        # if commands is not an iterable, make it one
        if not isinstance(commands, typing.Iterable):
            commands = [commands]

        for command in commands:
            try:
                self._exec_command(command)
            except (exceptions.Exit, exceptions.LoopBreak, exceptions.LoopContinue):
                raise
            except Exception as e:
                # Attach command to exception
                raise Exception(f"Error executing command: {command}") from e

    # Interprets and executes the YAML file, return exit code
    def run(self, script: str) -> int:
        # Parse YAML
        yaml = parsers.parse_yaml(script)

        self.error = None

        # Execute
        try:
            self.execute(yaml)
        except exceptions.Exit as e:
            logger.info(f"Exit with code {e.code}")
            return e.code
        except exceptions.LoopBreak:
            logger.error("Break outside of while loop")
            return -1
        except exceptions.LoopContinue:
            logger.error("Continue outside of while loop")
            return -1
        except Exception as e:
            self.error = e
            logger.error(f"Error: {e}")
            return -1

        return 0

    # Substitutes (evaluates) variables in a string
    # Variables to be substituted are in the form {{ expression }} (or expressions {{ var + 1 }})
    def eval_string(self, string: str) -> str:
        for match in INTERPOLATE_REGEX.finditer(string):
            value = self.eval_expr(match.group(1))  # evaluate the expressio
            string = string.replace(match.group(0), str(value))
        return string

    def eval_expr(
        self,
        expr: str,
        *,
        force_quotes: bool = False,  # Force quotes on strings
    ) -> typing.Any:
        if isinstance(expr, str):
            if force_quotes:
                expr = '"' + expr + '"'
            ret = eval(
                expr, {"__builtins__": BUILTINS}, self.variables
            )  # nosec: Secure eval, only allow safe builtins (arithmetics, and a few more)
        else:
            ret = expr
        return ret

    def set_variable(self, name: str, value: typing.Any) -> None:
        self.variables[name] = value
