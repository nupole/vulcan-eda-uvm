import dataclasses

from vulcan_eda.uvm.signals.bundle import Bundle

@dataclasses.dataclass(frozen=True)
class AxiStreamBeat:
    data: int
    last: bool

    @classmethod
    def signals(cls, data, last):
        return Bundle(data, last)

    def to_values(self):
        return (self.data, self.last)

    @classmethod
    def from_values(cls, values):
        data, last = values
        return cls(int(data), bool(last))
