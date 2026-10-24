import dataclasses

from vulcan_eda.uvm.generators.random_generator import RandomGenerator

@dataclasses.dataclass(frozen=True)
class RandomBooleanGenerator(RandomGenerator):
    pct_true: float

    def __post_init__(self):
        if not (0 < self.pct_true <= 100):
            raise ValueError("pct_true must be greater than 0 and at most 100")

    def _next(self, rng):
        return rng.random() * 100 < self.pct_true
