import dataclasses
import itertools

@dataclasses.dataclass(frozen=True)
class WalkingOneHotGenerator:
    width: int

    def __post_init__(self):
        if not (self.width > 0):
            raise ValueError("width must be positive")

    def __iter__(self):
        return itertools.cycle(1 << bit for bit in range(self.width))
