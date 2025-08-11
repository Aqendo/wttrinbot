import sqlalchemy.ext.asyncio
import telegram

from wttrinbot.models.context import WttrContext
from wttrinbot.models.saves import Saves
from wttrinbot.translations.ru import translation
from wttrinbot.utils.coord_resolver import resolve_coords
from wttrinbot.utils.direction import get_direction


async def answer_search(update: telegram.Update, context: WttrContext, query: str):
    place_coords = resolve_coords(context.Nominatim(), query)

    if not place_coords:
        return await update.inline_query.answer(
            [
                telegram.InlineQueryResultArticle(
                    id="-1",
                    title="Не смог найти такого места!",
                    input_message_content=telegram.InputTextMessageContent(
                        message_text="Не смог найти такого места!"
                    ),
                )
            ],
            is_personal=True,
            cache_time=0,
        )
    lat, lon = place_coords.latitude, place_coords.longitude
    async with context.ClientSession.get(
        f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
    ) as req:
        json1 = await req.json()
        info = json1["properties"]["timeseries"][0]["data"]["instant"]["details"]
        air_pressure = f"<b>Давление:</b> {round(info['air_pressure_at_sea_level']/1.333)} мм рт. ст."
        temp = f"<b>Температура:</b> {info['air_temperature']} °{'C' if json1['properties']['meta']['units']['air_temperature'] == 'celsius' else 'F'}"
        cloudy = f"<b>Облачность:</b> {info['cloud_area_fraction']}%"
        visibility = f"<b>Относительная влажность:</b> {info['relative_humidity']}%"
        wind_speed = f"<b>Скорость ветра:</b> {info['wind_speed']} м/с"
        wind_directions = (
            f"<b>Направление ветра:</b> {get_direction(info['wind_from_direction'])}"
        )
        weather_words = (
            translation.get(
                json1["properties"]["timeseries"][0]["data"]["next_1_hours"]["summary"][
                    "symbol_code"
                ]
            )
            or json1["properties"]["timeseries"][0]["data"]["next_1_hours"]["summary"][
                "symbol_code"
            ]
        )
        data = f"\n<b>{weather_words}</b>\n{air_pressure}\n{temp}\n{cloudy}\n{visibility}\n{wind_speed}\n{wind_directions}"
        address = place_coords.address
        if "ох" in address:
            # Censorship
            address = (
                place_coords.address.replace("Хохол", "Холм")
                .replace("хохол", "холм")
                .replace("хохл", "холм")
                .replace("Хохл", "Холм")
            )
        return await update.inline_query.answer(
            [
                telegram.InlineQueryResultArticle(
                    id="1",
                    title=address.split(",", maxsplit=1)[0][:20],
                    input_message_content=telegram.InputTextMessageContent(
                        message_text=f"<b>{address.split(',', maxsplit=1)[0]}</b>"
                        + data,
                        parse_mode="HTML",
                    ),
                ),
                telegram.InlineQueryResultArticle(
                    id="2",
                    title=address,
                    input_message_content=telegram.InputTextMessageContent(
                        message_text=f"<b>{address}</b>" + data,
                        parse_mode="HTML",
                    ),
                ),
                telegram.InlineQueryResultArticle(
                    id="3",
                    title="Показать анонимно (без локации)",
                    input_message_content=telegram.InputTextMessageContent(
                        message_text=data,
                        parse_mode="HTML",
                    ),
                ),
            ],
            cache_time=10,
            is_personal=False,
        )


async def inline_handler_saved_history(update: telegram.Update, context: WttrContext):
    async_sessionmaker: sqlalchemy.ext.asyncio.async_sessionmaker = (
        context.async_sessionmaker
    )

    session: sqlalchemy.ext.asyncio.AsyncSession
    async with async_sessionmaker() as session:
        result = await session.scalar(
            sqlalchemy.select(Saves).where(
                Saves.user == update.inline_query.from_user.id
            )
        )
        if not result:
            return await update.inline_query.answer(
                [
                    telegram.InlineQueryResultArticle(
                        id="-1",
                        title="Введи место/координаты чтобы узнать погоду там!",
                        input_message_content=telegram.InputTextMessageContent(
                            message_text="Введи место/координаты чтобы узнать погоду там!",
                        ),
                    )
                ],
                cache_time=0,
                is_personal=True,
            )

        return await answer_search(update, context, result.last_query)


async def inline_handler(update: telegram.Update, context: WttrContext):
    if not update.inline_query.query or update.inline_query.query.strip() == "":
        return await inline_handler_saved_history(update, context)
    return await answer_search(update, context, update.inline_query.query)


async def inline_feedback_handler(update: telegram.Update, context: WttrContext):
    if update.chosen_inline_result.result_id == "-1":
        return
    async with context.async_sessionmaker() as session:
        await session.merge(
            Saves(
                user=update.chosen_inline_result.from_user.id,
                last_query=update.chosen_inline_result.query,
            )
        )
        await session.commit()
