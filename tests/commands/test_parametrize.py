"""
test_parametrize.py - {summery}

{long description}

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from pytest import mark, fixture

from Modules.commands import command, parametrize, Rescue, trigger
from Modules.commands.rat_command import _flush, prefix
from Modules.context import Context

pytestmark = mark.cmd_parametrize


@fixture
def Setup_fx(bot_fx):
    """Sets up the test environment"""
    _flush()


@mark.usefixtures('Setup_fx')
@mark.asyncio
async def test_foo(bot_fx, rescue_sop_fx):
    # add a rescue to the board
    bot_fx.board.append(rescue_sop_fx)

    @parametrize
    @command('foo')
    async def cmd_foo(context: Context, bar: Rescue[int]):
        return 42


    ctx = await Context.from_message(bot_fx, "#unit_test", 'some_ov',
                               f"{prefix}foo {rescue_sop_fx.board_index}")

    retn = await trigger(ctx)

    pass