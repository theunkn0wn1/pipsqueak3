"""
_command.py - Command abstraction

Copyright (c) 2019 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
from __future__ import annotations

import logging
import typing
from dataclasses import dataclass, field

from ._exceptions import Abort, UsageError
from ..context import Context

# set the logger for rat_command
LOG = logging.getLogger(f"mecha.{__name__}")
_CALLABLE_TYPE = "typing.Callable[[Context, ...], typing.Any]"


@dataclass
class Command:
    underlying: _CALLABLE_TYPE
    usage: str = ""
    pre_execution_hooks: typing.List[_CALLABLE_TYPE] = field(default_factory=list)

    async def __call__(self, ctx: Context, *args, **kwargs):
        ...
        result = None
        try:
            result = await self.underlying(ctx=ctx, *args, **kwargs)
        except UsageError:
            # usage error
            await ctx.reply(self.usage)
        except Abort:
            await ctx.reply("Aborted!")

        finally:
            return result


async def uhh(ctx: Context, potaot: int):
    ...


# command = Command( underlying=uhh)
