import dataclasses

TAPS = {7: 6, 9: 5, 11: 9, 15: 14, 23: 18, 31: 28}

@dataclasses.dataclass(frozen=True)
class PrbsGenerator:
    order: int = 7
    width: int = 1
    start: int | None = None

    def __post_init__(self):
        if self.order not in TAPS:
            raise ValueError(f"order must be one of {', '.join(str(order) for order in TAPS)}")
        if not (self.width > 0):
            raise ValueError("width must be positive")
        if self.start is not None and not (0 < self.start < 2 ** self.order):
            raise ValueError("start must be non-zero and fit in order bits")

    def __iter__(self):
        mask = 2 ** self.order - 1
        tap = TAPS[self.order]
        state = mask if self.start is None else self.start
        while True:
            word = 0
            for _ in range(self.width):
                bit = (state >> (self.order - 1) ^ state >> (tap - 1)) & 1
                state = (state << 1 | bit) & mask
                word = word << 1 | bit
            yield word
