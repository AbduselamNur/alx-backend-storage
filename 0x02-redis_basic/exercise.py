#!/usr/bin/env python3
"""Writing strings to Redis"""
import redis
import uuid
from typing import Union, AnyStr, Optional, Callable
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """returns a Callable"""
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper for decorated function"""
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """returns a Callable"""
    input_list = method.__qualname__ + ":inputs"
    output_list = method.__qualname__ + ":outputs"

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper for decorated function"""
        self._redis.rpush(input_list, str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_list, output)
        return output

    return wrapper


def replay(method: Callable) -> None:
    """replay the history of calls of a particular function"""
    key = method.__qualname__
    cache = method.__self__
    count = cache._redis.get(key).decode('utf-8')
    inputs = cache._redis.lrange(key + ":inputs", 0, -1)
    outputs = cache._redis.lrange(key + ":outputs", 0, -1)
    print(f"{key} was called {count} times:")
    for i, o in zip(inputs, outputs):
        print(f"{key}(*{i.decode('utf-8')}) -> {o.decode('utf-8')}")


class Cache:
    """Cache class"""
    def __init__(self):
        """Constructor method"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store method"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[callable] = None) -> Union[
            str, bytes, int, float]:
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
