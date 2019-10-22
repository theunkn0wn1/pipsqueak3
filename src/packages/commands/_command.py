"""
_command.py - Command abstraction

Copyright (c) 2019 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md

This module is built on top of the Pydle system.

"""
from __future__ import annotations

import typing
from dataclasses import dataclass, field

from ._exceptions import Abort, UsageError
from ..context import Context
from loguru import logger

_CALLABLE_TYPE = "typing.Callable[[Context, ...], typing.Any]"


@dataclass
class Command:
    underlying: _CALLABLE_TYPE
    usage: str
    pre_execution_hooks: typing.List[_CALLABLE_TYPE] = field(default_factory=list)

    async def __call__(self, ctx: Context):
        logger.trace("entering command __call__")
        extra_args: typing.Dict[str, typing.Any] = {}

        result = None

        logger.trace("executing pre-execution hooks...")
        try:
            # invoke pre-execution hooks, anything returned by hooks
            # update the kwarg dict to call the underlying with
            for hook in self.pre_execution_hooks:
                logger.trace("executing pre-command hook {}", hook)
                result = await hook(ctx)
                logger.trace("done with hook {}", hook)
                logger.debug("pre-execution hook {} resulted in {}", hook, result)
                if result:
                    extra_args.update(result)

            logger.debug("calling underlying with extra_args:= {}", extra_args)
            await self.underlying(ctx, **extra_args)
        except UsageError:
            # usage error
            await ctx.reply(self.usage)
        except Abort:
            await ctx.reply("Aborted!")

        finally:
            return result
