import dataclasses

from vulcan_eda.uvm.data.formatted_data import FormattedData
from vulcan_eda.uvm.signals.bundle import Bundle
from vulcan_eda.uvm.signals.constant import Constant

@dataclasses.dataclass(frozen=True, kw_only=True)
class AxiWriteData(FormattedData):
    data: int = dataclasses.field(metadata={"format": "#x"})
    strobe: int = dataclasses.field(metadata={"format": "#x"})
    last: bool = True

    @classmethod
    def signals(cls, data, strobe, last=Constant(1)):
        return Bundle(data, strobe, last)

    def to_values(self):
        return (self.data, self.strobe, self.last)

    @classmethod
    def from_values(cls, values):
        data, strobe, last = values
        return cls(data=int(data), strobe=int(strobe), last=bool(last))
