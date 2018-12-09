"""
parametrize.py - Command parametrizer

Defines the `@parametrize` decorator for use with the Command system.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from inspect import getfullargspec
from logging import getLogger
from typing import Callable
from uuid import UUID

from Modules.context import Context
from Modules.rat import Rat as _Rat
from Modules.rat_rescue import Rescue as _Rescue
from .parsers import ArgumentParser
from .rat_command import _registered_commands
from .types import Rescue, Rat, Name, Word

log = getLogger(f"mecha.{__name__}")


def parametrize(func: Callable) -> Callable:
    """
    Marks a command definition for parametrization.

    This function will do some introspection magic on the function signature as to
    ascertain the types to create argument groups for, and update the command registrations
    accordingly.

    This decorator is designed to be **pass through**, meaning it does not wrap the `func`,
    thus allowing the decorated to be called outside the Command invocation machinery (eg by another
    command)

    Notes:
        This decorator **must** be applied **after** command registration
    Sanity checks:
        This decorator will perform some sanity checks on the decorated `func`
            - func **must** be a registered command
            - func **must** have a `context` argument
            - the `context` argument's type **must** be Context
            - all other arguments, excluding vargs and vkwargs, **must** have type annotations

    Args:
        func (Callable): function to parametrize

    Returns:
        func unmodified.

    Raises:
        AssertionError: any sanity check failed.


    Valid Examples:
        >>> from Modules.commands import command

        Note: Parametrize only works for functions decorated as commands

        >>> @parametrize
        ... @command('param_demo-1')
        ... def foo(context:Context, bar: int):
        ...     ...

    Invalid Examples:
            >>> @parametrize
            ... @command('param_demo-2')
            ... def no_context(bar:int):
            ...     ...
            Traceback (most recent call last):
                ...
            AssertionError: function must accept a context argument.

            >>> @parametrize
            ... @command('param_demo-3')
            ... def foo(context:int, bar:int):
            ...     ...
            Traceback (most recent call last):
                ...
            AssertionError: the `context` argument must be of type Context.

            >>> @parametrize
            ... @command('param_demo-4')
            ... def no_fun(context:Context, foo:int, bar):
            ...     ...
            Traceback (most recent call last):
                ...
            AssertionError: argument bar **must** have a defined type.
    """

    # get the func's specification
    spec = getfullargspec(func)

    # #################
    # Sanity checks
    # ######
    assert "context" in spec.args, "function must accept a context argument."
    assert "context" in spec.annotations, "the `context` argument must have a type hint."
    assert spec.annotations['context'] is Context, "the `context` argument must be of type Context."

    # build a list of arguments except for context
    arguments = [argument for argument in spec.args if argument != "context"]
    # types must be defined, assert sanity
    for arg in arguments:
        assert arg in spec.annotations, f"argument {arg} **must** have a defined type."

    # make a parser for the func, and use the func's name for the parser
    parser = ArgumentParser(prog=func.__name__)

    # #################
    # Argument group building
    # #####

    # we should stop getting into so many arguments, shouldn't we? :P

    # for each argument
    for argument in arguments:
        # get the argument's annotation
        annotation = spec.annotations[argument]

        if annotation is int:
            log.debug(f"adding int parsing group by name {argument}...")
            parser.add_argument(argument, type=int, help="a number")
            parser._parametrized_args[argument] = int

        elif annotation is Word:
            log.debug(f"adding word parsing group by name {argument}...")
            parser.add_argument(argument, type=str, help="a word")
            parser._parametrized_args[argument] = Word

        # check if we have a Rescue type
        elif annotation in [Rescue, Rescue[int], Rescue[str], Rescue[UUID], _Rescue,
                            Rescue[type(None)]]:
            # use an ugly hack to get the specified sub-type. Im not happy i need to touch a magic
            # here but its not publicly exposed and im NOT subclassing (move the shit elsewhere).
            # suggestions on how to access the subtype more clearly are welcome.

            if annotation in [Rescue, _Rescue]:
                subtype = None
            else:
                subtype = annotation.__args__[0]

            log.debug(
                f"adding Rescue parser group by the name {argument} with subtype {subtype}...")
            parser.add_rescue_param(argument, subtype)

        elif annotation in [Rat, _Rat, Rat[UUID], Rat[Name]]:
            if annotation in [Rat, _Rat]:
                subtype = None
            else:
                subtype = annotation.__args__[0]
            log.debug(f"adding Rat parser group by the name {argument} with subtype {subtype}...")
            parser.add_rescue_param(argument, subtype)

        else:
            raise RuntimeError

    # register the parser
    _registered_commands[func].parser = parser
    # return the original
    return func
