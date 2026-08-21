import httpx
from typing import Optional
from ..config import get_settings

settings = get_settings()

class AtlasClient:
    def __init__(self):
        self.base_url = settings.atlas_base_url
        self.agent_key = settings.atlas_agent_key

    async def _invoke(self, capability_id: str, input_data: dict) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/aimarket/invoke",
                json={"capability_id": capability_id, "input": input_data},
                headers={"X-Agent-Key": self.agent_key},
                timeout=10.0
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"ok": False, "error": f"Status {response.status_code}"}

    async def invoke_situation_brief(self, lat: float, lon: float) -> dict:
        # bbox around rounded lat/lon: 0.1 degree ~ 11 km
        return await self._invoke(
            "atlas.situation.brief@v1",
            {
                "north": lat + 0.1,
                "south": lat - 0.1,
                "east": lon + 0.1,
                "west": lon - 0.1,
                "layers": ["flood", "effis", "lightning", "volcano", "alerts", "events", "tsunami"],
                "locale": "en",
                "max_citations": 5
            }
        )

    async def invoke_fire_weather(self, lat: float, lon: float) -> dict:
        return await self._invoke(
            "atlas.fire.weather@v1",
            {
                "north": lat + 0.1,
                "south": lat - 0.1,
                "east": lon + 0.1,
                "west": lon - 0.1,
                "include_air": True,
                "limit": 10,
                "max_air_km": 50,
                "max_weather_km": 50
            }
        )

    async def invoke_nearest(self, lat: float, lon: float) -> dict:
        return await self._invoke(
            "atlas.nearest.read@v1",
            {
                "lat": lat,
                "lon": lon,
                "layers": ["flood", "effis"],
                "max_km": 100,
                "per_layer": 1
            }
        )
