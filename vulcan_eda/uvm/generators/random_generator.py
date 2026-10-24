import dataclasses
import random

@dataclasses.dataclass(frozen=True)
class RandomGenerator:
    seed: int | None = dataclasses.field(default=None, kw_only=True)

    def __iter__(self):
        rng = random.Random(random.getrandbits(64) if self.seed is None else self.seed)
        while True:
            yield self.next_value(rng)

    def next_value(self, rng):
        raise NotImplementedError
