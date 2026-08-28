# aicom-factory-atlas-core-layers
# aicom-factory-atlas-bbox
# aicom-factory-mesh-participant-runtime
from __future__ import annotations

from .aimarket_participant import get_participant


class AtlasClient:
    """Sentinel mesh client — Hub/AI-market participant (trial or paid channel)."""

    async def _invoke(self, capability_id: str, input_data: dict) -> dict:
        # AimarketParticipant.invoke is synchronous (urllib); do NOT call _invoke.
        return get_participant().invoke(capability_id, input_data)

    async def invoke_situation_brief(self, lat: float, lon: float) -> dict:
        return await self._invoke(
            "atlas.situation.brief@v1",
            {
                "north": lat + 5.0,
                "south": lat - 5.0,
                "east": lon + 5.0,
                "west": lon - 5.0,
                "layers": ["weather", "air", "fire", "flood", "effis", "lightning", "volcano", "alerts", "events", "tsunami"],
                "locale": "en",
                "max_citations": 5,
            },
        )

    async def invoke_fire_weather(self, lat: float, lon: float) -> dict:
        return await self._invoke(
            "atlas.fire.weather@v1",
            {
                "north": lat + 5.0,
                "south": lat - 5.0,
                "east": lon + 5.0,
                "west": lon - 5.0,
                "include_air": True,
                "limit": 10,
                "max_air_km": 50,
                "max_weather_km": 50,
            },
        )

    async def invoke_nearest(self, lat: float, lon: float) -> dict:
        return await self._invoke(
            "atlas.nearest.read@v1",
            {
                "lat": lat,
                "lon": lon,
                "layers": ["weather", "air", "fire", "flood", "effis"],
                "max_km": 500,
                "per_layer": 1,
            },
        )
