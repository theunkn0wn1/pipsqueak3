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
@mark.parametrize("subtype, method", [(int, 'board_index'),
                                      (UUID, 'uuid'),
                                      (Name, 'client'),
                                      ]
                  )
async def test_rescue_subtype(bot_fx, rescue_sop_fx, subtype, method):
    # add a rescue to the board
    bot_fx.board.append(rescue_sop_fx)

    @parametrize
    @command('foo')
    async def cmd_foo(context: Context, bar: _Rescue[subtype]):
        return bar

    ctx = await Context.from_message(bot_fx, "#unit_test", 'some_ov',
                                     f"{prefix}foo {getattr(rescue_sop_fx, method)}")

    retn = await trigger(ctx)

    assert retn is rescue_sop_fx


@mark.usefixtures('Setup_fx')
@mark.asyncio
@mark.parametrize("subtype", [Rescue, _Rescue])
@mark.parametrize('method', ['board_index',
                             'uuid',
                             'client'])
async def test_rescue_plain(bot_fx, rescue_sop_fx, subtype, method):
    # add a rescue to the board
    bot_fx.board.append(rescue_sop_fx)

    @parametrize
    @command('foo')
    async def cmd_foo(context: Context, bar: subtype):
        return bar

    # uuid's get a silly prefix, lets be sure to include it
    invocation = f"{prefix}foo {'@' if method == 'uuid' else ''}{getattr(rescue_sop_fx, method)}"
    ctx = await Context.from_message(bot_fx, "#unit_test", 'some_ov',
                                     invocation)

    retn = await trigger(ctx)

    assert retn is rescue_sop_fx


@mark.usefixtures('Setup_fx')
@mark.asyncio
async def test_help(bot_fx):
    """
    Verifies a help menu is appended to the parametrized command
    Args:
        bot_fx ():
        rescue_plain_fx ():

    Returns:

    """

    @parametrize
    @command('foo')
    async def cmd_foo(context: Context):
        return 42

    bot_fx.sent_messages.clear()
    ctx = await Context.from_message(bot_fx, "#unit_test", 'some_ov',
                                     f"{prefix}foo -h")

    retn = await trigger(ctx)

    assert retn is None
    # assert a message got emitted
    assert bot_fx.sent_messages
