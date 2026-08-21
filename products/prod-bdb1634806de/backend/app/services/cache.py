import time
from typing import Any, Optional

class CacheService:
    def __init__(self):
        self._store = {}
        self._ttl = 600  # 10 minutes default

    def get(self, lat: float, lon: float) -> Optional[Any]:
        key = f"{lat:.1f}:{lon:.1f}"
        item = self._store.get(key)
        if item and item["expires_at"] > time.time():
            return item["value"]
        return None

    def set(self, lat: float, lon: float, value: Any, ttl: int = None):
        if ttl is None:
            ttl = self._ttl
        key = f"{lat:.1f}:{lon:.1f}"
        self._store[key] = {"value": value, "expires_at": time.time() + ttl}

    def clear(self):
        self._store.clear()
