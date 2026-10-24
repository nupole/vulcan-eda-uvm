import dataclasses
import typing

from vulcan_eda.uvm.signals.signal import Signal

@dataclasses.dataclass(frozen=True)
class RandomSignalGenerator:
    signal: typing.Any

    def __post_init__(self):
        object.__setattr__(self, "signal", Signal.wrap(self.signal))

    def __iter__(self):
        while True:
            yield self.signal.random_value()
