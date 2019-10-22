"""
tesT_board.py  - tests for the board commands suite.

Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import logging

import pytest

from src.commands import board as board_commands
from src.packages.context import Context
from src.packages.utils import Platforms

LOG = logging.getLogger(f"mecha.{__name__}")

pytestmark = [pytest.mark.unit, pytest.mark.commands, pytest.mark.asyncio, pytest.mark.board_commands]


@pytest.mark.parametrize("name", ('lordBusiness22', 'sicklyTadpole', 'WHATS_GOIN_ON'))
@pytest.mark.parametrize("platform", [
    ('pc', Platforms.PC),
    ('Pc', Platforms.PC),
    ('ps', Platforms.PS),
    ('xb', Platforms.XB),
    ('XB', Platforms.XB),
    ('XBoX', Platforms.XB)
])
async def test_inject_create(bot_fx, rat_board_fx, name, platform, random_string_fx):
    platform_str, expected = platform
    context = await Context.from_message(bot_fx,
                                         "#fuelrats",
                                         "some_admin",
                                         f"!inject {name} {platform_str} {random_string_fx}"
                                         )

    await board_commands.cmd_inject(context)

    assert name in rat_board_fx

    assert rat_board_fx[name].platform is expected, "platform mismatch!"


async def test_inject_existing(bot_fx, rat_board_fx, rescue_sop_fx):
    # append existing rescue from fixture into the board
    await rat_board_fx.append(rescue_sop_fx)
    payload = f"!inject {rescue_sop_fx.client} update data is updated!"
    context = await Context.from_message(bot_fx, "#fuelrats", "some_ov", payload)

    await board_commands.cmd_inject(context)

    assert len(rat_board_fx) == 1, "inject made a second case...."


@pytest.mark.parametrize("initial_state", [True, False])
@pytest.mark.parametrize("method", ["client", "board_index", "api_id"])
async def test_code_red(bot_fx, rat_board_fx, rescue_sop_fx, method, initial_state):
    rescue_sop_fx.code_red = initial_state
    await rat_board_fx.append(rescue_sop_fx)

    payload = f"!cr {getattr(rescue_sop_fx, method)}"
    context = await Context.from_message(bot_fx, "#fuelrats", "some_rat", payload)

    await board_commands.cmd_code_red(context)

    assert rescue_sop_fx.code_red != initial_state

    response = bot_fx.sent_messages[0]['message']
    assert "CODE RED" if not initial_state else "no longer" in response, \
        f"bad response received := '{response}'"


async def test_code_red_miss(bot_fx, rat_board_fx):
    payload = "!cr bigRedButton"
    context = await Context.from_message(bot_fx, "#fuelrats", "some_rat", payload)

    await board_commands.cmd_code_red(context)

    assert "Unable to find" in bot_fx.sent_messages[0]['message']
