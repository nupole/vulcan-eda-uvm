import dataclasses

from vulcan_eda.uvm.generators.random_generator import RandomGenerator

@dataclasses.dataclass(frozen=True)
class RandomBitsGenerator(RandomGenerator):
    width: int

    def __post_init__(self):
        if not (self.width > 0):
            raise ValueError("width must be positive")

    def next_value(self, rng):
        return rng.getrandbits(self.width)
