from __future__ import annotations
import attr
import pytest

from src.packages.commands.command_abc import CommandABC
from src.packages.context import Context
from src.packages.rescue import Rescue

pytestmark = [pytest.mark.asyncio, pytest.mark.commands]


async def test_conversions(bot_fx, rat_board_fx, rescue_sop_fx, async_callable_fx):
    bot_fx.board = rat_board_fx
    await rat_board_fx.append(rescue_sop_fx)

    @attr.dataclass
    class CmdInject(CommandABC):
        case: Rescue
        usage = "inject usage"

        async def __call__(self):
            await async_callable_fx()

    context = await Context.from_message(bot_fx, "#unittest", "some_ov",
                                         f"inject {rescue_sop_fx.board_index}")

    invocation = CmdInject.from_ctx(ctx=context, parametrize=True)
    assert invocation.case is rescue_sop_fx
    await invocation()
    assert async_callable_fx.was_called
