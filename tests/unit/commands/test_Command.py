from src.packages.commands._command import Command
from src.packages.commands._exceptions import Abort, UsageError
import pytest


@pytest.mark.asyncio
async def test_abort(bot_fx, context_fx, async_callable_fx, random_string_fx):
    cmd = Command(f"cmd_{random_string_fx}", usage="usage text")
    cmd.underlying = async_callable_fx
    async_callable_fx.exception_to_raise = Abort
    await cmd.invoke(context_fx)

    assert async_callable_fx.was_called
    assert "aborted" in bot_fx.sent_messages[0]['message'].casefold()


@pytest.mark.asyncio
async def test_usage_error(bot_fx, context_fx, async_callable_fx, random_string_fx):
    cmd = Command(f"cmd_{random_string_fx}", usage="usage text")
    cmd.underlying = async_callable_fx
    async_callable_fx.exception_to_raise = UsageError
    await cmd.invoke(context_fx)

    assert async_callable_fx.was_called
    assert "usage" in bot_fx.sent_messages[0]['message'].casefold()
