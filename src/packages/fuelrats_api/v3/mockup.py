import json
import typing
from uuid import UUID

import aiohttp
import attr
from loguru import logger

from src.packages.rat import Rat
from src.packages.rescue import Rescue
from ._converters import RatConverter, RescueConverter
from .._base import ApiABC


class ApiError(RuntimeError):
    ...


@attr.s
class MockupAPI(ApiABC):
    # name overrides
    rat_converter = RatConverter
    rescue_converter = RescueConverter

    # post init behaviors
    def __attrs_post_init__(self):
        self.RAT_ENDPOINT = f"{self.url}/rats"
        self.RESCUE_ENDPOINT = f"{self.url}/rescues"

    # internals
    @staticmethod
    async def _query(method: str, query: str, **kwargs):
        logger.debug('[{method}] {query}', method=method, query=query)
        async with aiohttp.ClientSession() as session:
            async with session.request(method=method, url=query, **kwargs) as response:
                data = await response.json()
                logger.debug("api response := {}", data)
                if response.status != 200:
                    raise ApiError(response.status)
                return data

    # interface implementation

    async def get_rescues(self) -> typing.List[Rescue]:
        query = self.RESCUE_ENDPOINT

        json = await self._query(method="GET", query=query)
        # json will be a list of API rescue objects.
        # Parse this into our internal representation.
        return [self.rescue_converter.from_api(item) for item in json]

    async def get_rescue(self, uuid: UUID) -> Rescue:
        query = f"{self.RESCUE_ENDPOINT}/{uuid}"
        json = await self._query(method='GET', query=query)
        return self.rescue_converter.from_api(json)

    async def update_rescue(self, rescue: Rescue) -> None:
        query = f"{self.RESCUE_ENDPOINT}/{rescue.api_id}"
        data = self.rescue_converter.to_api(rescue)
        logger.debug("update data := {}", data)
        result = await self._query(method='PATCH', query=query, data=json.dumps(data),
                                   skip_auto_headers={'CONTENT-TYPE'})

    async def get_rat(self, key: typing.Union[UUID, str]) -> Rat:
        if isinstance(key, UUID):
            query = f"{self.RAT_ENDPOINT}/{key}"
            json = await self._query(method='GET', query=query)
        elif isinstance(key, str):
            query = f"{self.RAT_ENDPOINT}?filter=[name:eq]={key}"
            json = await self._query(method='GET', query=query)

        else:
            raise TypeError(key)

        return self.rat_converter.from_api(json)
