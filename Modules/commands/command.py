"""
command.py - Command object

Defines a Command object, part of the command processing mechanism.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

"""

from logging import getLogger
from typing import Any, Callable, Optional

from Modules.context import Context
from .parsers import ArgumentParser, ParserWantsExit

# set the logger for rat_command
log = getLogger(f"mecha.{__name__}")


class Command:
    def __init__(self, func: Callable, parser: Optional[ArgumentParser] = None):

        # func doesn't get a setter, so we do the check here.
        if not callable(func):
            raise ValueError("func must be callable.")

        self._func = func
        self._parser = None

        if parser is not None:
            # call the setter as to avoid duplicating type checks
            self.parser = parser

    async def __call__(self, context: Context, *args, **kwargs) -> Any:
        """
        Call the underlying function
        """

        if self.parser:
            namespace = self.parser.parse_args(context.words)
            log.debug(f"namespace={namespace}")

        return await self._func(context=context, *args, **kwargs)

    @property
    def parser(self) -> Optional[ArgumentParser]:
        """
        The parser associated with this Command object, if any.
        """
        return self._parser

    @parser.setter
    def parser(self, value: Optional[ArgumentParser]):
        if not (isinstance(value, ArgumentParser)):
            raise TypeError(f"expected an instance of ArgumentParser, got {type(value)}")

        self._parser = value
