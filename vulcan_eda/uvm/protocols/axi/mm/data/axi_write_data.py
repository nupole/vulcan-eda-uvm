import dataclasses

from vulcan_eda.uvm.signals.bundle import Bundle
from vulcan_eda.uvm.signals.constant import Constant

@dataclasses.dataclass(frozen=True)
class AxiWriteData:
    data: int
    strobe: int
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
