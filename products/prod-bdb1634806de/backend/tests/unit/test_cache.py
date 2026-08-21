from app.services.cache import CacheService

def test_cache_set_get():
    cache = CacheService()
    cache.set(10.1, 20.2, {"foo": "bar"})
    assert cache.get(10.1, 20.2) == {"foo": "bar"}

def test_cache_expiry():
    import time
    cache = CacheService()
    cache.set(10.1, 20.2, {"foo": "bar"}, ttl=1)
    time.sleep(1.1)
    assert cache.get(10.1, 20.2) is None
