from typing import Callable

import telegram.ext
from aiohttp import ClientSession
from geopy import Nominatim
from sqlalchemy.ext.asyncio import async_sessionmaker


class WttrContext(telegram.ext.CallbackContext):
    @property
    def async_sessionmaker(self) -> async_sessionmaker:
        return self.bot_data["async_sessionmaker"]

    @property
    def ClientSession(self) -> ClientSession:
        return self.bot_data["ClientSession"]

    @property
    def Nominatim(self) -> Callable[[], Nominatim]:
        return self.bot_data["Nominatim"]
