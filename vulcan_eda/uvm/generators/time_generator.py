import dataclasses

import cocotb.simtime

UNITS = ("step", "fs", "ps", "ns", "us", "ms", "sec")

@dataclasses.dataclass(frozen=True)
class TimeGenerator:
    unit: str = "ns"

    def __post_init__(self):
        if self.unit not in UNITS:
            raise ValueError(f"unit must be one of {', '.join(UNITS)}")

    def __iter__(self):
        while True:
            yield int(cocotb.simtime.get_sim_time(self.unit))
