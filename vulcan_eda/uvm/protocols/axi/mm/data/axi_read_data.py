import dataclasses

from vulcan_eda.uvm.protocols.axi.mm.data.axi_response import AxiResponse
from vulcan_eda.uvm.signals.bundle import Bundle
from vulcan_eda.uvm.signals.constant import Constant

@dataclasses.dataclass(frozen=True)
class AxiReadData:
    data: int
    response: AxiResponse
    last: bool = True
    id: int = 0

    @classmethod
    def signals(cls, data, response, id=Constant(0), last=Constant(1)):
        return Bundle(id, data, response, last)

    def to_values(self):
        return (self.id, self.data, self.response.value, self.last)

    @classmethod
    def from_values(cls, values):
        txn_id, data, response, last = values
        return cls(data=int(data), response=AxiResponse(int(response)), last=bool(last), id=int(txn_id))
