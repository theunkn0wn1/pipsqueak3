"""
__name__.py - Parametrize namespace

Namespace for all things Parametrize.

Includes type definitions and the decorator itself.

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from .types import Rescue, Rat, Name, Index
from .parametrize import parametrize
from .rat_command import command
from .types import Rescue, Rat, Name, Index

__all__ = [
    "Rescue",
    "Rat",
    "Name",
    "Index",
    "parametrize",
    "command",
]
