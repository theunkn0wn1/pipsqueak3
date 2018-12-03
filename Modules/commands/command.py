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
from uuid import UUID

from Modules.context import Context
from .parsers import ArgumentParser
from .types import Rescue

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
            # if we have a registered parser, call it
            if '-h' in context.words:
                # help condition, bail out
                return await context.reply(self.parser.format_help())

            # normal invocation, parse the arguments
            namespace = self.parser.parse_args(context.words[1:])
            log.debug(f"namespace={namespace}")

            for name, value_type in self.parser._types.items():
                value = getattr(namespace, name)

                if value_type is Rescue[None]:
                    # any rescue type
                    kwargs[name] = context.bot.board.search(value)
                elif value_type is Rescue[int]:
                    # board index
                    kwargs[name] = context.bot.board.find_by_index(value)

                elif value_type is Rescue[UUID]:
                    # by uuid
                    kwargs[name] = context.bot.board.find_by_uuid(value)

        # todo parse namespace -> target variables
        return await self._func(context=context, *args, **kwargs)

    @property
    def parser(self) -> Optional[ArgumentParser]:
        """
        The parser associated with this Command object, if any.
        """
        return self._parser

    @parser.setter
    def parser(self, value: ArgumentParser):
        if not (isinstance(value, ArgumentParser)):
            raise TypeError(f"expected an instance of ArgumentParser, got {type(value)}")

        self._parser = value
