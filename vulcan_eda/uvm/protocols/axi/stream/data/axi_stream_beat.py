import dataclasses

from vulcan_eda.uvm.data.formatted_data import FormattedData
from vulcan_eda.uvm.signals.bundle import Bundle

@dataclasses.dataclass(frozen=True, kw_only=True)
class AxiStreamBeat(FormattedData):
    data: int = dataclasses.field(metadata={"format": "#x"})
    last: bool

    @classmethod
    def signals(cls, data, last):
        return Bundle(data, last)

    def to_values(self):
        return (self.data, self.last)

    @classmethod
    def from_values(cls, values):
        data, last = values
        return cls(data=int(data), last=bool(last))
