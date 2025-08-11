from typing import Any

import geopy


def resolve_coords(decoder: geopy.Nominatim, query: str) -> None | Any:
    place_coords = decoder.geocode(query)
    if not place_coords:
        return None
    return place_coords
