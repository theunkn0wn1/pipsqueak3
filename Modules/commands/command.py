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

from argparse import REMAINDER
from Modules.context import Context
from Modules.rat_rescue import Rescue as _Rescue
from .parsers import ArgumentParser, ParserError
from .types import Rescue, Name, Rat, Index, Word

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
        Parametrize the arguments and call the underlying function
        """

        if self.parser:
            # if we have a registered parser, call it
            if '-h' in context.words:
                # help condition, bail out
                return await context.reply(self.parser.format_help())

            # normal invocation, parse the arguments
            try:
                namespace = self.parser.parse_args(context.words[1:])
            except ParserError as exc:
                # something went wrong during parsing, reply the error message
                await context.reply(exc.args[0])
                return

            log.debug(f"namespace={namespace}")
            # iterate over the parametrized arguments
            for name, value_type in self.parser._parametrized_args.items():
                # get the parsed value
                target = getattr(namespace, name)
                # ugly case/switch style block is ugly

                if value_type in [Word, int, REMAINDER]:
                    # simple types
                    kwargs[name] = target
                # if the Rescue is a plain Rescue type, just search
                elif value_type in [Rescue[type(None)], _Rescue]:
                    # any rescue
                    kwargs[name] = context.bot.board.search(target)

                elif value_type is Rescue[Index]:
                    # rescue by board index
                    kwargs[name] = context.bot.board.find_by_index(target)

                elif value_type is Rescue[Name]:
                    # rescue by client name
                    kwargs[name] = context.bot.board.find_by_name(target)

                elif value_type is Rescue[UUID]:
                    # rescue by uuid
                    kwargs[name] = context.bot.board.find_by_uuid(target)

                elif value_type is Rat:
                    kwargs[name] = await context.bot.rat_cache.get_rat(target)

                elif value_type is Rat[UUID]:
                    kwargs[name] = await context.bot.rat_cache.get_rat_by_uuid(target)

                elif value_type is Rat[Name]:
                    kwargs[name] = await context.bot.rat_cache.get_rat_by_name(target)

                ...

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
