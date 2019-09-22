"""
_exceptions.py - Exceptions that can be raised during a command invocation with special meaning

Copyright (c) 2019 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""


class CommandException(Exception):
    """
    Base exception for Command processing signals
    """


class Abort(CommandException):
    """
    Invoked command was aborted. this is not necessarily due to an error state
    """


class UsageError(Abort):
    """
    Usage error, return command usage and then abort
    """
