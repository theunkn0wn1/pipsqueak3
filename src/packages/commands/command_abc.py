from __future__ import annotations

import collections
import typing
import uuid
from abc import ABC, abstractmethod

import attr
from loguru import logger

from ..context import Context
from ..rescue import Rescue


class UsageError(ValueError):
    """ incorrect command usage """

@attr.dataclass
class CommandABC(ABC):
    ctx: Context
    usage: typing.ClassVar[str]

    @abstractmethod
    async def __call__(self, *args, **kwargs):
        ...

    @staticmethod
    def get_rescue(ctx: Context, key=None) -> Rescue:
        try:
            if key not in ctx.bot.board:
                rescue = ctx.bot.board[int(key)]
            else:
                rescue = ctx.bot.board.get(key)
        except (KeyError, ValueError):
            try:
                force_uuid = uuid.UUID(key)
            except ValueError:
                return None
            else:
                rescue = ctx.bot.board.get(force_uuid)

        return rescue

    @classmethod
    def from_ctx(cls, ctx: Context, parametrize: bool = False):
        if not parametrize:
            return cls(ctx, *ctx.words[1:])

        words = collections.deque(ctx.words[1:])

        kwargs = {}

        for field in attr.fields(cls):
            if field.type == 'Context':
                kwargs[field.name] = ctx

            elif field.type == "Rescue":
                kwargs[field.name] = cls.get_rescue(ctx, words.popleft())

            else:
                # unknown type
                logger.warning("using str and 1 word for unregistered field type {!r}", field.type)
                kwargs[field.name] = words.popleft()
        if len(words):
            # unconsumed arguments
            raise UsageError
        return cls(**kwargs)
