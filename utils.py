from typing import Iterator

def get_bit_positions(n:int) -> Iterator[int]:
    while n:
        b:int = n & (~n+1)
        yield b
        n ^= b