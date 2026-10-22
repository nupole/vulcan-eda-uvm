import dataclasses

@dataclasses.dataclass(frozen=True)
class RandomDataSequenceConfig:
    max_data: int = 255

    def __post_init__(self):
        if self.max_data < 0:
            raise ValueError("max_data must not be negative")
