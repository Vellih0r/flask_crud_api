import redis
import cache_config
from typing import Optional
from json import loads

r = redis.Redis(host=cache_config.host, port=cache_config.port, decode_responses=True)

def get_key(key: str):
    try:
        out = r.get(key)
    except Exception as e:
        pritn(f'Exception {e}')
        return
    return loads(out)

def get_keys() -> Optional[dict]:
    try:
        keys = r.keys('*')
        out = [loads(r.get(key)) for key in keys]
    except Exception as e:
        print(f'Exception {e}')
        return
    return out

def setex_key(key: str, value: str, time: int = 10) -> str:
    """Sets value to a key and expiration time(default tim = 10)"""
    try:
        ttl = r.ttl(key)
        if ttl != -2:
            return f'Key {key} is alive, ttl : {ttl}'
        r.setex(key, time, value)
    except Exception as e:
        print(f'Exception {e}')
        return
    print(f'Success created key {key}')
    return

def del_key(key: str) -> None:
    try:
        r.delete(key)
    except Exception as e:
        print(f'Exception {e}')
        return
    print(f'Sucess delete {key}')
    return

def del_keys() -> None:
    try:
        r.flushall()
    except Exception as e:
        print(f'Exception {e}')
        return
    print(f'Sucess delete all')
    return