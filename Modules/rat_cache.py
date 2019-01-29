"""
rat_cache.py - Caching facilities for Rat

Provides a caching facility for Rat, allowing created Rat to be reused without further API
Queries.

Copyright (c) 2018 The Fuel Rat Mischief,
All rights reserved.

Licensed under the BSD 3-Clause License.

See LICENSE.md
"""
from collections import abc
from typing import Iterator, Union, Dict, Set, NoReturn, Optional
from uuid import UUID

from Modules.rat import Rat
from utils.ratlib import Platforms

_KeyType = Union[str, UUID]
_ValueType = Rat


class RatCache(abc.Mapping, abc.Container):
    """
    The RatCache. Caches rats the bot has seen before for easy access later.

    also provides some "get" methods for retrieving rats from the API
    """
    __slots__ = ['_by_uuid', '_by_name', '_items', '_api_handler']

    def __init__(self, api_handler=None):
        """
        Creates a new Rat Cache.
        Args:
            api_handler ():
        """
        self._by_uuid: Dict[UUID, _ValueType] = {}
        self._by_name: Dict[str, _ValueType] = {}
        self._items: Set[Rat] = set()
        self._api_handler = api_handler

    def __contains__(self, item: Union[_ValueType, _KeyType]):
        # true if its an item, or a valid key
        return item in self._items or item in self._by_uuid or item in self._by_name

    def __setitem__(self, key: _KeyType, value: _ValueType) -> None:
        if not isinstance(value, Rat):
            # if the value isn't a rat bail out.
            raise ValueError(f"object of type{type(value)} is not supported.")

        # regardless of the key, always add the value to items
        self._items.add(value)

        if isinstance(key, str):
            # type is a name

            self._by_uuid[value.uuid] = value  # append to UUIDs
            self._by_name[key] = value  # append to names

        elif isinstance(key, UUID):
            self._by_uuid[key] = value  # append to UUIDs
            self._by_name[value.name] = value  # append to names
        else:
            return NotImplemented

    def __getitem__(self, key: _KeyType) -> _ValueType:
        # if its not in us, raise
        if key not in self:
            raise KeyError(key)

        # its either a name or a UUID
        if key in self._by_name:
            return self._by_name[key]
        else:
            return self._by_uuid[key]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[_KeyType]:
        return iter(self._by_name)

    def add(self, value: Rat) -> NoReturn:
        """
        Appends a new rat to the cache

        Convenience wrapper.

        Args:
            value (Rat): rat object to append
        """

        self[value.name] = value

    def clear(self) -> NoReturn:
        self._items.clear()
        self._by_name.clear()
        self._by_uuid.clear()

    async def get_rat_by_name(self,
                              name: str,
                              platform: Optional[Platforms] = None) -> Optional[Rat]:
        """
        Retrieves a rat from the API by its specified name and, optionally, restricted to a platform

        Args:
            name (str): target name to search for
            platform(Platforms): Platform to narrow search to

        Returns:
            Rat object, if a rat was found.

        Note:
            this will not return any local instances of a matching rat, use :meth:`__getitem__` instead.
        """
        raise NotImplementedError("retrieving rats from the API  is presently not implemented!")

    async def get_rat_by_uuid(self, uuid) -> Optional[Rat]:
        """
        Retrieve a rat from the API by its specified uuid (rat id)

        Args:
            uuid (UUID): rat id of target rat

        Returns:
            Rat object, if a rat was found.
        """
        raise NotImplementedError("retrieving rats from the API  is presently not implemented!")

