import dataclasses

@dataclasses.dataclass(frozen=True)
class RandomDataSequenceConfig:
    min_data: int = 0
    max_data: int = 255

    def __post_init__(self):
        if not (self.min_data <= self.max_data):
            raise ValueError("min_data must not be greater than max_data")
