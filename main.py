import aiohttp
import fastapi
from fastapi.responses import JSONResponse
from geopy import Nominatim
import json
decoder = Nominatim(user_agent="wttrinbot_telegram")
import math
from weather_whats_now import translations
app = fastapi.FastAPI()
session = None

def get_direction(degrees):
    DIRECTIONS = [
        'С', 'ССВ', 'СВ', 'ВСВ', 'В', 'ВЮВ', 'ЮВ', 'ЮЮВ', 'Ю', 'ЮЮЗ', 'ЮЗ', 'ЗЮЗ',
        'З', 'ЗСЗ', 'СЗ', 'ССЗ', 'С'
    ]
    return DIRECTIONS[round(degrees / 22.5)]

@app.post("/")
async def wttr(request: fastapi.Request):
    json_telegram = await request.json()
    place = json_telegram["inline_query"]["query"]
    global session
    if not session:
        session = aiohttp.ClientSession()
    if place == "":
        return JSONResponse({
            "method": "answerInlineQuery",
            "inline_query_id": json_telegram["inline_query"]["id"],
            "results": json.dumps([
                {
                    "type": "article",
                    "id": "1",
                    "title": "хз какой тебе город надо",
                    "input_message_content": {
                        "message_text": f"ты город не указал ALOOOO🔉🔉🔉🔉🔉🔉🔉",
                        "parse_mode": "HTML"
                    },
                }
            ]),
            "cache_time": 0,
            "is_personal": True,
        })
    place_coords = decoder.geocode(place)
    try:
        lat = place_coords.latitude
        lon = place_coords.longitude
    except:
        return JSONResponse({
            "method": "answerInlineQuery",
            "inline_query_id": json_telegram["inline_query"]["id"],
            "results": json.dumps([
                {
                    "type": "article",
                    "id": "1",
                    "title": "не нашёл такого места :(((((((",
                    "input_message_content": {
                        "message_text": "не нашёл места с таким именем",
                        "parse_mode": "HTML"
                    },
                }
            ]),
            "cache_time": 100,
            "is_personal": False,
        })
    async with session.get(
        f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat}&lon={lon}"
    ) as req:
        json1 = await req.json()
        #print(type(json1), json1["properties"]["timeseries"][0]["data"])
        info = json1["properties"]["timeseries"][0]["data"]["instant"]["details"]
        air_pressure = f"<b>Давление:</b> {round(info['air_pressure_at_sea_level']/1.333)} мм рт. ст."
        temp = f"<b>Температура:</b> {info['air_temperature']} °{'C' if json1['properties']['meta']['units']['air_temperature'] == 'celsius' else 'F'}"
        cloudy = f"<b>Облачность:</b> {info['cloud_area_fraction']}%"
        visibility = f"<b>Относительная влажность:</b> {info['relative_humidity']}%"
        wind_speed = f"<b>Скорость ветра:</b> {info['wind_speed']} м/с"
        wind_directions = f"<b>Направление ветра:</b> {get_direction(info['wind_from_direction'])}"
        weather_words = translations.get(json1["properties"]["timeseries"][0]["data"]["next_1_hours"]["summary"]["symbol_code"]) or json1["properties"]["timeseries"][0]["data"]["next_1_hours"]["summary"]["symbol_code"]
        #print(place_coords)
        data = f"\n<b>{weather_words}</b>\n{air_pressure}\n{temp}\n{cloudy}\n{visibility}\n{wind_speed}\n{wind_directions}"
        address = place_coords.address
        if "ох" in address:
            address = place_coords.address.replace('Хохлы', 'Холмы').replace("Хохол", "Холм").replace("хохол","холм")
        return JSONResponse({
            "method": "answerInlineQuery",
            "inline_query_id": json_telegram["inline_query"]["id"],
            "results": json.dumps([
                {
                    "type": "article",
                    "id": "1",
                    "title": f"С именем локации коротко {address.split(',', maxsplit=1)[0][:20]}",
                    "input_message_content": {
                        "message_text": f"<b>{address.split(',', maxsplit=1)[0]}</b>"+data,
                        "parse_mode": "HTML"
                    },
                },
                 {
                    "type": "article",
                    "id": "2",
                    "title": f"С именем локации фулл {address}",
                    "input_message_content": {
                        "message_text": f"<b>{address}</b>"+data,
                        "parse_mode": "HTML"
                    },
                },
                 {
                    "type": "article",
                    "id": "3",
                    "title": "Без имени локации (ананимнаст)",
                    "input_message_content": {
                        "message_text": data,
                        "parse_mode": "HTML"
                    }
                }
            ]),
            "cache_time": 0,
            "is_personal": True,
        })


@app.on_event("shutdown")
async def shutdown_event():
    if session:
        await session.close()
