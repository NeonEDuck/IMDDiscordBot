from typing import Iterator
from datetime import datetime, timedelta

def get_bit_positions(n :int) -> Iterator[int]:
    while n:
        b :int = n & (~n+1)
        yield b
        n ^= b

def utc_plus(hours :int) -> datetime:
    return datetime.utcnow() + timedelta(hours=hours)