"""
test_parametrize.py - {summery}

{long description}

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from uuid import UUID

from pytest import mark, fixture

from Modules.commands import command, parametrize, Rescue as _Rescue, trigger, Name
from Modules.commands.rat_command import _flush, prefix
from Modules.context import Context
from Modules.rat_rescue import Rescue

pytestmark = mark.cmd_parametrize


@fixture
def Setup_fx(bot_fx):
    """Sets up the test environment"""
    _flush()


@mark.usefixtures('Setup_fx')
@mark.asyncio
@mark.parametrize("subtype, func", [(int, 'board_index'),
                                    (UUID, 'uuid'),
                                    (Name, 'client'),
                                    ]
                  )
async def test_rescue_subtype(bot_fx, rescue_sop_fx, subtype, func):
    # add a rescue to the board
    bot_fx.board.append(rescue_sop_fx)

    @parametrize
    @command('foo')
    async def cmd_foo(context: Context, bar: _Rescue[subtype]):
        return bar

    ctx = await Context.from_message(bot_fx, "#unit_test", 'some_ov',
                                     f"{prefix}foo {getattr(rescue_sop_fx, func)}")

    retn = await trigger(ctx)

    assert retn is rescue_sop_fx


@mark.usefixtures('Setup_fx')
@mark.asyncio
@mark.parametrize("subtype", [Rescue, _Rescue])
@mark.parametrize('func', ['board_index',
                           'uuid',
                           'client'])
async def test_rescue_plain(bot_fx, rescue_sop_fx, subtype, func):
    # add a rescue to the board
    bot_fx.board.append(rescue_sop_fx)

    @parametrize
    @command('foo')
    async def cmd_foo(context: Context, bar: subtype):
        return bar

    # uuid's get a silly prefix, lets be sure to include it
    invocation = f"{prefix}foo {'@' if func == 'uuid' else ''}{getattr(rescue_sop_fx, func)}"
    ctx = await Context.from_message(bot_fx, "#unit_test", 'some_ov',
                                     invocation)

    retn = await trigger(ctx)

    assert retn is rescue_sop_fx


@mark.usefixtures('Setup_fx')
@mark.asyncio
async def test_rescue_help(bot_fx, rescue_sop_fx):
    # add a rescue to the board
    bot_fx.board.append(rescue_sop_fx)

    @parametrize
    @command('foo')
    async def cmd_foo(context: Context, bar: _Rescue[int]):
        return bar

    bot_fx.sent_messages.clear()
    ctx = await Context.from_message(bot_fx, "#unit_test", 'some_ov',
                                     f"{prefix}foo -h")

    retn = await trigger(ctx)

    assert retn is None
    # assert a message got emitted
    assert bot_fx.sent_messages
