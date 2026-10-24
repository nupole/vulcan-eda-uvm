import dataclasses
import random

@dataclasses.dataclass(frozen=True)
class RandomIntegerGenerator:
    min_value: int
    max_value: int
    seed: int | None = None

    def __post_init__(self):
        if not (self.min_value <= self.max_value):
            raise ValueError("min_value must not be greater than max_value")

    def __iter__(self):
        rng = random.Random(random.getrandbits(64) if self.seed is None else self.seed)
        while True:
            yield rng.randint(self.min_value, self.max_value)
