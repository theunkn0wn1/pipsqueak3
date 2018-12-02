"""
rat_command.py - Handles Command registration and Command-triggering IRC events

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""

import logging
from typing import Callable, Any, NoReturn, Dict

from Modules.context import Context
from Modules.rules import get_rule, clear_rules
from config import config
from . import Command

_registered_commands: Dict[str, Command] = {}
"""
Registered Commands
"""
# set the logger for rat_command
log = logging.getLogger(f"mecha.{__name__}")


class CommandException(Exception):
    """
    base Command Exception
    """
    pass


class InvalidCommandException(CommandException):
    """
    invoked command failed validation
    """
    pass


class NameCollisionException(CommandException):
    """
    Someone attempted to register a command already registered.
    """
    pass


# character/s that must prefix a message for it to be parsed as a command.
prefix = config['commands']['prefix']


async def trigger(ctx) -> Any:
    """

    Args:
        ctx (Context): Invocation context

    Returns:
        result of command execution
    """

    if ctx.words_eol[0] == "":
        return  # empty message, bail out

    if ctx.prefixed:
        if ctx.words[0].casefold() in _registered_commands:
            # A regular command
            command_fun = _registered_commands[ctx.words[0].casefold()]
            extra_args = ()
            log.debug(f"Regular command {ctx.words[0]} invoked.")
        else:
            # Might be a regular rule
            command_fun, extra_args = get_rule(ctx.words, ctx.words_eol, prefixless=False)
            if command_fun:
                log.debug(
                    f"Rule {getattr(command_fun, '__name__', '')} matching {ctx.words[0]} found.")
            else:
                log.debug(f"Could not find command or rule for {prefix}{ctx.words[0]}.")
    else:
        # Might still be a prefixless rule
        command_fun, extra_args = get_rule(ctx.words, ctx.words_eol, prefixless=True)
        if command_fun:
            log.debug(
                f"Prefixless rule {getattr(command_fun, '__name__', '')} matching {ctx.words[0]} "
                f"found.")

    if command_fun:
        return await command_fun(ctx, *extra_args)
    else:
        log.debug(f"Ignoring message '{ctx.words_eol[0]}'. Not a command or rule.")


def _register(func, names: list or str) -> NoReturn:
    """
    Register a new command
    :param func: function
    :param names: names to registerx
    """
    assert func is not None and callable(func), "`func` must be callable."

    if isinstance(names, str):
        names = [names]  # idiot proofing

    # transform commands to lowercase
    names = [name.casefold() for name in names]

    # build a Command object to register

    cmd = Command(func)
    for alias in names:
        if alias in _registered_commands:
            # command already registered
            raise NameCollisionException(f"attempted to re-register command(s) {alias}")
        else:
            formed_dict = {alias: cmd}
            _registered_commands.update(formed_dict)


def _flush() -> None:
    """
    Flushes registered commands
    Probably useless outside testing...
    """

    _registered_commands.clear()
    clear_rules()


def command(*aliases):
    """
    Registers a command by aliases

    Args:
        *aliases ([str]): aliases to register

    """

    def real_decorator(func: Callable):
        """
        The actual commands decorator

        Args:
            func (Callable): wrapped function

        Returns:
            Callable: *func*, unmodified.
        """
        log.debug(f"Registering command aliases: {aliases}...")
        _register(func, aliases)
        log.debug(f"Registration of {aliases} completed.")

        return func

    return real_decorator
