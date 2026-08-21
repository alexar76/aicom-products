import time
from collections import defaultdict
from fastapi import Request, HTTPException

_rate_store = defaultdict(list)

def rate_limit(max_requests: int, window_seconds: int):
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()
            requests = _rate_store[client_ip]
            # remove old
            _rate_store[client_ip] = [t for t in requests if now - t < window_seconds]
            if len(_rate_store[client_ip]) >= max_requests:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            _rate_store[client_ip].append(now)
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
