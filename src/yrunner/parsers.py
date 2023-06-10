import typing
import enum
import yaml

# parses a command, and return a list of tokens
# We do this with a simple state machine
# 1. We start in the "normal" state
# 2. If it's a quote, we switch to the "quoted" state
#   2.1. If it's a quote (or single quote, same as starting), we switch back to the "normal" state and add the token to the list
#   2.2. If it's a backslash, we switch to the "escaped" state
#     2.2.1. If it's a quote (or single quote), we add it to the current token
#     2.2.2. If it's a backslash, we add a backslash to the current token
#     basic \n, \t, \r, \b, \f, \v are supported
#   2.3. Anything else is added to the current token
# 3. If it's a space and we're in the "normal" state, we add the token to the list
# anything else is added to the current token
def parse_command(command: str) -> typing.List[str]:
    class State(enum.IntEnum):
        NORMAL = 0
        QUOTED = 1
        ESCAPED = 2

    tokens = []
    quote: str = ""
    current_token = ""   # nosec: command token, not a password
    state = State.NORMAL
    for c in command:
        if state == State.NORMAL:
            if c == " ":
                if current_token:
                    tokens.append(current_token)
                    current_token = ""  # nosec: current_token is not a password
            elif c in ["'", '"']:
                current_token += c
                quote = c
                state = State.QUOTED
            else:
                current_token += c
        elif state == State.QUOTED:
            if c == "\\":
                state = State.ESCAPED
            elif c == quote:
                current_token += c
                tokens.append(current_token)
                current_token = ""  # nosec: current_token is not a password
                state = State.NORMAL
            else:
                current_token += c
        elif state == State.ESCAPED:
            if c == "n":
                current_token += '\n'
            elif c == "t":
                current_token += '\t'
            elif c == "r":
                current_token += '\r'
            elif c == "b":
                current_token += '\b'
            elif c == "f":
                current_token += '\f'
            elif c == "v":
                current_token += '\v'
            elif c == "\\":
                current_token += '\\'
            elif c == quote:
                current_token += quote
            else:
                current_token += '\\' + c
            state = State.QUOTED
        else:
            raise Exception("Invalid state")

    if state == State.QUOTED:
        raise Exception("Invalid state (missing closing quote)")

    if current_token:
        tokens.append(current_token)

    return tokens

def parse_yaml(yaml_data: str) -> typing.Any:
    return yaml.safe_load(yaml_data)

