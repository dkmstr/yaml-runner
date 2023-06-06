# Copyright (c) 2023 Adolfo Gómez García <dkmaster@dkmon.com>
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

class YRunnerException(Exception):
    pass


class YRunnerInvalidCommand(YRunnerException):
    pass

class YRunnerInvalidParameter(YRunnerException):
    pass

class YRunnerInvalidContent(YRunnerException):
    pass

# Not exceptions, used to control the flow of the program


# To catch break on while loops
class LoopBreak(YRunnerException):
    pass


# To catch continue on while loops
class LoopContinue(YRunnerException):
    pass


# To catch exit
class Exit(YRunnerException):
    def __init__(self, code: int) -> None:
        self.code = code
