"""
parsers.py - Argument parsers for Commands

Defines argument parsers for the Commands machinery.
At the core is a custom ArgumentParser, which was necessary to avoid calling sys.exit() whenever
someone fails an argument parsing / uses -h >..>

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from argparse import ArgumentParser as QuittingArgumentParser
from logging import getLogger
from typing import NoReturn, Type, Dict, Optional
from uuid import UUID

from .types import Rescue, Name, Index, _RatType

log = getLogger(f"mecha.{__name__}")


class ParserError(Exception):
    """
    Something (probably)went wrong during command parsing.
    """
    ...


class ParserWantsExit(ParserError):
    """
    Raised when the parser wants to terminate the parsing prematurely (but not erroneously)
    """


class ArgumentParser(QuittingArgumentParser):

    def __init__(self, *args, **kwargs):
        self._parametrized_args: Dict[str, Type] = {}
        """mapping between positional arguments and their parametrized types"""
        super().__init__(*args, **kwargs)

    # TODO: help support
    def error(self, message: str) -> NoReturn:
        log.debug(f"intercepted attempt to exit. message={message}")
        raise ParserError(message)

    def exit(self, status: int = 0, message="") -> NoReturn:
        # lol no, we ain't calling sys.exit(). log the call >..>
        log.debug(f"intercepted attempt to exit. status={status}\tmessage={message}")
        # and raise a catchable exception
        raise ParserWantsExit(message)

    def print_help(self, file=None):
        log.debug(f"intercepted help exit signal, data = {self.format_help()}")

    def add_rescue_param(self, name: str, validate_type: Type = None):
        """
        Adds a positional Rescue parsing group

        Args:
            name(str): name of the positional argument
            validate_type(Type): Type to validate the argument as
        """
        if validate_type is None or type(None):  # no subtype
            help_str = "irc name of client, the API uuid, or the case number of the Rescue."
        elif validate_type is Name:  # name subtype
            help_str = "irc name of the client"
        elif validate_type is UUID:  # api id subtype
            help_str = "API id of rescue"
        elif validate_type is Index:  # case number subtype
            help_str = "case number of Rescue"

        else:
            raise ValueError(f"unknown Rescue subtype {validate_type}")

        # append argument to the types variable
        self._parametrized_args[name] = Rescue[validate_type]

        return self.add_argument(name, type=validate_type, help=help_str)

    def add_rat_param(self, name: str, validate_type: Optional[_RatType]):
        """
        Appends a Rat parser group.

        Args:
            name (str): argument Name
            validate_type (_RatType): validation type

        Returns:

        """
        if validate_type is None:
            help_str = "Name of rat, or its rat id"
        elif validate_type is Name:
            help_str = "Name of rat"
        elif validate_type is UUID:
            help_str = "api id of rat"
        else:
            raise ValueError(f"unknown Rat subtype {type(validate_type)}")

        self._parametrized_args[name] = _RatType[validate_type]
        return self.add_argument(name, type=validate_type, help=help_str)
