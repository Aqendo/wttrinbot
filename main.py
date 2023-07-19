import aiohttp
from aiogram import Bot, Dispatcher, Router, types

bot = Bot("6119150508:AAGtxN5ZIJCpFJvDcZA0narLW6Ysst0o20Q", parse_mode="HTML")
from geopy import Nominatim

decoder = Nominatim(user_agent="wttrinbot_telegram")
router = Router()

session = None

@router.inline_query()
async def wttr(query: types.InlineQuery):
    global session
    if not session:
        session = aiohttp.ClientSession()
    place = query.query
    if place == "":
        return query.answer(
            [
                types.InlineQueryResultArticle(
                    id="1",
                    title="хз какой тебе город надо",
                    input_message_content=types.InputTextMessageContent(
                        message_text=f"ты город не указал ALOOOO🔉🔉🔉🔉🔉🔉🔉"
                    ),
                )
            ],
            cache_time=0,
            is_personal=True,
        )
    place_coords = decoder.geocode(place)
    try:
        lat = place_coords.latitude
        lon = place_coords.longitude
    except:
        return query.answer(
            [
                types.InlineQueryResultArticle(
                    id="1",
                    title="не нашёл такого места :(((((((",
                    input_message_content=types.InputTextMessageContent(
                        message_text=f"не нашёл места с таким именем"
                    ),
                )
            ],
            cache_time=0,
            is_personal=True,
        )
    async with session.get(
        f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
    ) as req:
        json = await req.json()
        print(type(json), json["properties"]["timeseries"][0]["data"])
        info = json["properties"]["timeseries"][0]["data"]["instant"]["details"]
        air_pressure = f"<b>Давление:</b> {info['air_pressure_at_sea_level']} гПа"
        temp = f"<b>Температура:</b> {info['air_temperature']} °{'C' if json['properties']['meta']['units']['air_temperature'] == 'celsius' else 'F'}"
        cloudy = f"<b>Облачность:</b> {info['cloud_area_fraction']}%"
        visibility = f"<b>Относительная влажность:</b> {info['relative_humidity']}%"
        wind_speed = f"<b>Скорость ветра:</b> {info['wind_speed']} м/с"
        print(place_coords)
        await query.answer(
            [
                types.InlineQueryResultArticle(
                    id="1",
                    title=f"С именем локации коротко {place_coords.address.split(',', maxsplit=1)[0][:20]}",
                    input_message_content=types.InputTextMessageContent(
                        message_text=f"<b>{place_coords.address.split(',', maxsplit=1)[0].replace('Хохлы', 'Холмы')}</b>\n{air_pressure}\n{temp}\n{cloudy}\n{visibility}\n{wind_speed}"
                    ),
                ),
                types.InlineQueryResultArticle(
                    id="2",
                    title=f"С именем локацииф фулл {place_coords.address}",
                    input_message_content=types.InputTextMessageContent(
                        message_text=f"<b>{place_coords.address.replace('Хохлы', 'Холмы')}</b>\n{air_pressure}\n{temp}\n{cloudy}\n{visibility}\n{wind_speed}"
                    ),
                ),
                types.InlineQueryResultArticle(
                    id="3",
                    title="Без имени локации (ананимнаст)",
                    input_message_content=types.InputTextMessageContent(
                        message_text=f"{air_pressure}\n{temp}\n{cloudy}\n{visibility}\n{wind_speed}"
                    ),
                ),
            ],
            cache_time=0,
            is_personal=True,
        )


async def main():
    session = aiohttp.ClientSession()
    dp = Dispatcher()
    dp.include_router(router)
    try:
        await dp.start_polling(bot)
    finally:
        await session.close()


import asyncio

asyncio.run(main())
asyncio.run(session.close())
