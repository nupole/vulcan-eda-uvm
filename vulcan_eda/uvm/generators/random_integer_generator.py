import dataclasses

from vulcan_eda.uvm.generators.random_generator import RandomGenerator

@dataclasses.dataclass(frozen=True)
class RandomIntegerGenerator(RandomGenerator):
    min_value: int
    max_value: int

    def __post_init__(self):
        if not (self.min_value <= self.max_value):
            raise ValueError("min_value must not be greater than max_value")

    def _next(self, rng):
        return rng.randint(self.min_value, self.max_value)
