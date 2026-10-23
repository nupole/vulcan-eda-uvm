import dataclasses

@dataclasses.dataclass(frozen=True)
class AxiStreamPacketSequenceConfig:
    num_packets: int = 10
    min_num_beats: int = 1
    max_num_beats: int = 16

    def __post_init__(self):
        if not (self.num_packets > 0):
            raise ValueError("num_packets must be positive")
        if not (self.min_num_beats > 0):
            raise ValueError("min_num_beats must be positive")
        if not (self.min_num_beats <= self.max_num_beats):
            raise ValueError("min_num_beats must not be greater than max_num_beats")
