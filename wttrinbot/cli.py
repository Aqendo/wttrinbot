import logging
import os
import ssl
import sys

import aiohttp
import dotenv
import geopy.geocoders
import sqlalchemy.ext.asyncio
import telegram
import telegram.ext

from wttrinbot.handlers.inline import inline_feedback_handler, inline_handler
from wttrinbot.models.base import Base
from wttrinbot.models.context import WttrContext
from wttrinbot.utils.check_env import check_env
from wttrinbot.utils.encode_sha1 import encode_sha1

dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.WARNING
)


async def post_init(_application: telegram.ext.Application) -> None:
    engine = sqlalchemy.ext.asyncio.create_async_engine(
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}",
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_sessionmaker = sqlalchemy.ext.asyncio.async_sessionmaker(
        engine, expire_on_commit=False
    )
    _application.bot_data["async_sessionmaker"] = async_sessionmaker

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    geopy.geocoders.options.default_ssl_context = ctx

    _application.bot_data["Nominatim"] = lambda: geopy.Nominatim(
        user_agent=encode_sha1(TOKEN + "_weatherbot")
    )

    _application.bot_data["ClientSession"] = aiohttp.ClientSession()


def run_bot():
    check_env()

    context_types = telegram.ext.ContextTypes(context=WttrContext)

    application = (
        telegram.ext.ApplicationBuilder()
        .token(TOKEN)
        .context_types(context_types)
        .post_init(post_init)
        .build()
    )

    application.add_handler(telegram.ext.InlineQueryHandler(inline_handler))
    application.add_handler(
        telegram.ext.ChosenInlineResultHandler(inline_feedback_handler)
    )

    application.run_polling(
        allowed_updates=["message", "inline_query", "chosen_inline_result"]
    )


if __name__ == "__main__":
    print("ERROR: cli.py should NOT be called directly", file=sys.stderr)
    sys.exit(1)
