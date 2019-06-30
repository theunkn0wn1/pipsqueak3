"""
tesT_board.py  - tests for the board commands suite.

Copyright (c) 2019 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""

import logging

from src.commands import administration
from src.packages.context import Context

import pytest
from src.commands import board as board_commands

LOG = logging.getLogger(f"mecha.{__name__}")

pytestmark = [pytest.mark.unit, pytest.mark.commands, pytest.mark.asyncio, pytest.mark.board_commands]


@pytest.mark.parametrize("name", ('lordBusiness22', 'sicklyTadpole', 'WHATS_GOIN_ON'))
@pytest.mark.parametrize("platform", ('pc', 'Pc', 'ps', 'xb', 'XB'))
async def test_inject_create(bot_fx, rat_board_fx, name, platform, random_string_fx):
    context = await Context.from_message(bot_fx,
                                         "#fuelrats",
                                         "some_admin",
                                         f"!inject {name} {platform} {random_string_fx}"
                                         )

    await board_commands.cmd_inject(context)

    assert name in rat_board_fx
