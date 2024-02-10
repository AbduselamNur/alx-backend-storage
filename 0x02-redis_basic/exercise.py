#!/usr/bin/env python3
"""Writing strings to Redis"""
import redis
import uuid
from typing import Union, AnyStr, Optional, Callable
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Count calls decorator"""
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper method"""
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper

class Cache:
    """Cache class"""
    def __init__(self):
        """Constructor method"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store method"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
    
    def get(self, key: str, fn: Optional[callable] = None) -> Union[str, bytes, int, float]:
        """Get method"""
        data = self._redis.get(key)
        if fn:
            return fn(data)
        return data
    
    def get_str(self, data: bytes) -> str:
        """Get str method"""
        return data.decode('utf-8')
    
    def get_int(self, data: bytes) -> int:
        """Get int method"""
        return int.from_bytes(data, byteorder='big')
