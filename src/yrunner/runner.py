import typing
import re
import logging

from . import parsers, types, exceptions
from . executors import internal

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

# Invalid content re (to secure builtins, we check that no xxx.__identifier__ is used)
INVALID_CONTENT_RE: typing.Final[re.Pattern] = re.compile(r'__\w+__')


class YRunner:
    commands: typing.Dict[str, types.Command]
    variables: typing.MutableMapping[str, typing.Any]
    error: typing.Optional[Exception] = None

    def __init__(
        self,
        *extra_commands: typing.Union[typing.List[types.Command], types.Command],
        variables: typing.Optional[typing.MutableMapping[str, typing.Any]] = None,
    ) -> None:
        # copy COMMANDS to self.commands
        self.commands = {command.name: command for command in internal.COMMANDS}
        for command in extra_commands:  # Can override existing commands
            if isinstance(command, list):
                for cmd in command:
                    self.commands[cmd.name] = cmd  
            else:
                self.commands[command.name] = command

        if variables is None:
            variables = {}

        self.variables = variables  # reference to the variables

    def _exec_command(self, node: typing.Mapping[str, typing.Any]) -> None:
        # Node must have only one key
        if isinstance(node, str):  # Simple command
            command_name = node
        else:
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
            except exceptions.YRunnerException:
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
        # if matchs invalid strings, raise exception indicating that and the string found
        if isinstance(expr, str):
            # Look for invalid strings
            match_invalid = INVALID_CONTENT_RE.search(expr)
            if match_invalid is not None:
                # Get the invalid string
                invalid_string = match_invalid.group(0)
                raise exceptions.YRunnerInvalidContent(f"Invalid content in {expr}: {invalid_string}")
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
