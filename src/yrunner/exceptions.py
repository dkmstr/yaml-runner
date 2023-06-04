class YRunnerError(Exception):
    pass


class YRunnerInvalidCommand(YRunnerError):
    pass

class YRunnerInvalidParameter(YRunnerError):
    pass

class YRunnerInvalidString(YRunnerError):
    pass

# Not exceptions, used to control the flow of the program


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
