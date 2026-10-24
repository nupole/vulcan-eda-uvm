import dataclasses

from vulcan_eda.uvm.protocols.axi.mm.data.axi_response import AxiResponse
from vulcan_eda.uvm.signals.bundle import Bundle
from vulcan_eda.uvm.signals.constant import Constant

@dataclasses.dataclass(frozen=True, kw_only=True)
class AxiWriteResponse:
    response: AxiResponse
    id: int = 0

    @classmethod
    def signals(cls, response, id=Constant(0)):
        return Bundle(id, response)

    def to_values(self):
        return (self.id, self.response.value)

    @classmethod
    def from_values(cls, values):
        txn_id, response = values
        return cls(response=AxiResponse(int(response)), id=int(txn_id))
