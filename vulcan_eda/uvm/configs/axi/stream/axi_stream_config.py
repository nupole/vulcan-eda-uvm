import dataclasses

@dataclasses.dataclass(frozen=True)
class AxiStreamConfig:
    num_bytes: int

    def __post_init__(self):
        if not (self.num_bytes > 0):
            raise ValueError("num_bytes must be positive")
