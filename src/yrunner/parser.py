import typing
import enum
import re
import yaml

# Simple tokenizer of an expression

# Token types, the value is the tupe operator, precedence, evaluator
class TokenType(enum.Enum):
    # Operators
    # Logical
    OR = ("or", 1, lambda stack:  stack.append(any([stack.pop(), stack.pop()])))
    OR2 = ("||", 1, lambda stack: stack.append(any([stack.pop(), stack.pop()])))
    AND = ("and", 2, lambda stack: stack.append(all([stack.pop(), stack.pop()])))
    AND2 = ("&&", 2, lambda stack: stack.append(all([stack.pop(), stack.pop()])))
    NOT = ("not", 7, lambda stack: stack.append(not stack.pop()))
    # Comparison
    EQ = ("==", 3, lambda stack: stack.append(stack.pop() == stack.pop()))
    NE = ("!=", 3, lambda stack: stack.append(stack.pop() != stack.pop()))
    LT = ("<", 3, lambda stack: stack.append(stack.pop(-2) < stack.pop()))
    GT = (">", 3, lambda stack: stack.append(stack.pop(-2) > stack.pop()))
    LE = ("<=", 3, lambda stack: stack.append(stack.pop(-2) <= stack.pop()))
    GE = (">=", 3, lambda stack: stack.append(stack.pop(-2) >= stack.pop()))
    # Arithmetic
    PLUS = ("+", 4, lambda stack: stack.append(stack.pop(-2) + stack.pop()))
    MINUS = ("-", 4, lambda stack: stack.append(stack.pop(-2) - stack.pop()))
    TIMES = ("*", 5, lambda stack: stack.append(stack.pop(-2) * stack.pop()))
    DIVIDE = ("/", 5, lambda stack: stack.append(stack.pop(-2) / stack.pop()))
    MOD = ("%", 5, lambda stack: stack.append(stack.pop(-2) % stack.pop()))
    POW = ("**", 6, lambda stack: stack.append(stack.pop(-2) ** stack.pop()))
    # Negative number
    NEG = ("NEG", 7, lambda stack: stack.append(-stack.pop()))

    # Parenthesis
    LPAREN = ("(", -1, None)
    RPAREN = (")", -1, None)
    # Other
    NUMBER = ("NUMBER", -1, None)
    STRING = ("STRING", -1, None)
    VARIABLE = ("VARIABLE", -1, None)

class Token(typing.NamedTuple):
    type: TokenType
    value: typing.Any


UNARY_OPERATORS: typing.Final[typing.Dict[str, TokenType]] = {
    '-': TokenType.NEG,
    'not': TokenType.NOT,
    '!': TokenType.NOT,
}

VALID_OPERATORS: typing.Final[typing.Dict[str, TokenType]] = {
    i.value[0]: i for i in TokenType if i not in [TokenType.NUMBER, TokenType.STRING, TokenType.VARIABLE]
}

# Tokenize an expression, taking into account strings, numbers (positive and negative), parenthesis and operators
def tokenize(expression: str) -> typing.List[Token]:
    class State(enum.IntEnum):
        NORMAL = 0
        QUOTED = 1
        ESCAPED = 2

    tokens: typing.List[Token] = []
    quote: str = ""
    current_token = ""   # nosec: command token, not a password
    state = State.NORMAL

    def append_number_or_string(current_token: str, tokens: typing.List[Token]):
        if current_token:
            # if an integer
            if re.match(r"^-?\d+$", current_token):
                tokens.append(Token(TokenType.NUMBER, int(current_token)))
            elif re.match(r"^-?\d+\.\d+$", current_token):  # float
                tokens.append(Token(TokenType.NUMBER, float(current_token)))
            else:
                tokens.append(Token(TokenType.VARIABLE, current_token))

    i = 0
    while i < len(expression):
        c = expression[i]
        if state == State.NORMAL:
            if c.isspace():
                # skip
                pass
            elif c in ["'", '"']:
                # Skip the quote
                quote = c
                state = State.QUOTED
            else:
                for op in VALID_OPERATORS:
                    if expression[i:].startswith(op):
                        if current_token:
                            append_number_or_string(current_token, tokens)
                            tokens.append(Token(VALID_OPERATORS[op], op))
                        else: # Unary operator, can only be negative or not
                            if op not in UNARY_OPERATORS:
                                raise Exception(f'Invalid unary operator {op} at pos {i}: {tokens}')
                            tokens.append(Token(UNARY_OPERATORS[op], op))
                        current_token = ""  # nosec: current_token is not a password
                        # Skip the operator
                        i += len(op) - 1
                        c = ''
                        break
                current_token += c
                    
        elif state == State.QUOTED:
            if c == "\\":
                state = State.ESCAPED
            elif c == quote:
                tokens.append(Token(TokenType.STRING, current_token))
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
        
        i += 1

    if state == State.QUOTED:
        raise Exception("Invalid state (missing closing quote)")

    if current_token:
        append_number_or_string(current_token, tokens)

    return tokens
    
def rpn_expression(tokens: typing.List[Token]) -> typing.List[Token]:
    output: typing.List[Token] = []
    stack: typing.List[Token] = []

    for token in tokens:
        if token.type in [TokenType.NUMBER, TokenType.STRING, TokenType.VARIABLE]:
            output.append(token)
        elif token.type == TokenType.LPAREN:
            stack.append(token)
        elif token.type == TokenType.RPAREN:
            while stack and stack[-1].type != TokenType.LPAREN:
                output.append(stack.pop())
            if not stack:
                raise Exception("Mismatched parenthesis")
            stack.pop()
        else:
            while stack and stack[-1].type != TokenType.LPAREN and token.type.value[1] <= stack[-1].type.value[1]:
                output.append(stack.pop())
            stack.append(token)

    while stack:
        if stack[-1].type == TokenType.LPAREN:
            raise Exception("Mismatched parenthesis")
        output.append(stack.pop())

    return output

def eval_expression(expression: str, variables: typing.Mapping[str, typing.Any]) -> typing.Any:
    tokens = tokenize(expression)
    rpn = rpn_expression(tokens)
    stack: typing.List[typing.Any] = []

    for token in rpn:
        if token.type in [TokenType.NUMBER, TokenType.STRING]:
            stack.append(token.value)
        elif token.type == TokenType.VARIABLE:
            if token.value in variables:
                stack.append(variables[token.value])
            else:
                raise Exception(f"Unknown variable {token.value}")
        else:
            evaluator = token.type.value[2]
            if evaluator:
                evaluator(stack)

    if len(stack) != 1:
        raise Exception(f"Invalid expression: {expression} (stack: {stack})")

    return stack[0]