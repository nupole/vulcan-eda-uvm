import dataclasses

from vulcan_eda.uvm.configs.base_config import BaseConfig

@dataclasses.dataclass(frozen=True)
class AxiStreamConfig(BaseConfig):
    num_bytes: int

    @classmethod
    def from_tdata(cls, tdata):
        if not (len(tdata) % 8 == 0):
            raise ValueError("tdata width must be a multiple of 8")
        return cls(num_bytes=len(tdata) // 8)

    def __post_init__(self):
        if not (self.num_bytes > 0):
            raise ValueError("num_bytes must be positive")
