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
from typing import NoReturn

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

    # TODO: help support
    def error(self, message: str) -> NoReturn:
        log.debug(f"intercepted attempt to exit. message={message}")
        raise ParserError(message)

    def exit(self, status: int = 0, message="") -> NoReturn:
        # lol no, we ain't calling sys.exit(). log the call >..>
        log.debug(f"intercepted attempt to exit. status={status}\tmessage={message}")
        # and raise a catchable exception
        raise ParserWantsExit(message)


def add_rescue_parsing_group(parser: ArgumentParser, name: str, validate_type) -> NoReturn:
    """
    Adds a positional Rescue parsing group
    Args:
        parser (ArgumentParser): Parser to add the group too
        name(str): name of the positional argument
        validate_type(Any): Type to validate the argument as

    Returns:

    """
    parser.add_argument(name, type=validate_type)
