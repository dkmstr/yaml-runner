# Copyright (c) 2023 Adolfo Gómez García <dkmaster@dkmon.com>
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT
import typing

if typing.TYPE_CHECKING:
    from .runner import YRunner

ExecutorType = typing.Callable[[typing.Mapping[str, typing.Any], 'YRunner'], None]

class CommandParameter(typing.NamedTuple):
    name: str
    optional: bool = False
    default: typing.Any = None


class Command(typing.NamedTuple):
    name: str
    executor: ExecutorType
    parameters: typing.Optional[
        typing.List[CommandParameter]
    ] = []  # None means any parameter, empty list means no parameters
