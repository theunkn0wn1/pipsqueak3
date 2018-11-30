"""
parametrize.py - Command parametrizer

Defines the `@parametrize` decorator for use with the Command system.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from inspect import getfullargspec
from typing import Callable

from Modules.context import Context


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
        >>> @parametrize
        ... def foo(context:Context, bar: int):
        ...     ...

    Invalid Examples:
            >>> @parametrize
            ... def no_context(bar:int):
            ...     ...
            Traceback (most recent call last):
                ...
            AssertionError: function must accept a context argument.

            >>> @parametrize
            ... def foo(context:int, bar:int):
            ...     ...
            Traceback (most recent call last):
                ...
            AssertionError: the `context` argument must be of type Context.

            >>> @parametrize
            ... def no_fun(context:Context, foo:int, bar):
            ...     ...
            Traceback (most recent call last):
                ...
            AssertionError: argument bar **must** have a defined type.
    """

    # get the func's specification
    spec = getfullargspec(func)

    assert "context" in spec.args, "function must accept a context argument."
    assert spec.annotations['context'] is Context, "the `context` argument must be of type Context."

    # build a list of arguments except for context and iterate over it
    for arg in [argument for argument in spec.args if argument != "context"]:
        assert arg in spec.annotations, f"argument {arg} **must** have a defined type."

    # return the original
    return func
