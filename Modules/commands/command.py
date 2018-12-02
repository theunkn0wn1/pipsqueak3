"""
command.py - Command object

Defines a Command object, part of the command processing mechanism.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

"""

from typing import Any, Callable, Optional

from .parsers import ArgumentParser


class Command:
    def __init__(self, func: Callable, parser: Optional[ArgumentParser] = None):

        # func doesn't get a setter, so we do the check here.
        if not callable(func):
            raise ValueError("func must be callable.")

        self._func = func
        self._parser = None

        # call the setter as to avoid duplicating type checks
        self.parser = parser

    def __call__(self, *args, **kwargs) -> Any:
        """
        Call the underlying function
        """
        return self._func(*args, **kwargs)

    @property
    def parser(self) -> Optional[ArgumentParser]:
        """
        The parser associated with this Command object, if any.
        """
        return self._parser

    @parser.setter
    def parser(self, value: Optional[ArgumentParser]):
        if (value is not None) and not (isinstance(value, ArgumentParser)):
            raise TypeError(f"expected an instance of ArgumentParser, got {type(value)}")

        self._parser = value
