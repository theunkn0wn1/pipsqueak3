"""
test_rat_cache.py - tests the rat_cache

Copyright (c) 2018 The Fuel Rats Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from uuid import uuid4

import pytest

from Modules.rat import Rat
from Modules.rat_cache import RatCache
from utils.ratlib import Platforms

pytestmark = pytest.mark.asyncio


async def test_get_name_existing(rat_good_fx: Rat, rat_cache_fx):
    """
    Verifies that cached rats can be found by name
    """
    found_rat = rat_cache_fx[rat_good_fx.name]
    assert rat_good_fx is found_rat



@pytest.mark.parametrize("actual, invalids", [
    (Platforms.XB, [Platforms.PC, Platforms.PS]),
    (Platforms.PC, [Platforms.XB, Platforms.PS]),
    (Platforms.PS, [Platforms.PC, Platforms.XB])
])
@pytest.mark.xfail  # tests dependent on feature not yet implemented.
async def test_find_rat_incorrect_platform(rat_cache_fx, actual, invalids):
    """
    Verifies that `Rat.get_rat_by_name` called with a specific platform that does not match
        the stored platform returns None
    """
    Rat(name="UNIT_TEST", uuid=None, platform=actual)
    for platform in invalids:
        found_rat = await rat_cache_fx.get_rat_by_name(name="UNIT_TEST", platform=platform)

        assert found_rat is None


@pytest.mark.xfail  # tests dependent on feature not yet implemented.
async def test_find_rat_by_name_not_existing(rat_cache_fx):
    """
    Verifies a cache miss on ratname returns None
    """
    found = await rat_cache_fx.get_rat_by_name(name="uhhh")
    assert found is None

    found = await rat_cache_fx.get_rat_by_name(name="chapstix", platform=Platforms.XB)
    assert found is None


async def test_clear(rat_cache_fx: RatCache):
    rat_cache_fx._by_name = {"s": 12}
    rat_cache_fx._by_uuid = {uuid4(): 12}

    rat_cache_fx.clear()
    assert {} == rat_cache_fx._by_uuid
    assert {} == rat_cache_fx._by_name
