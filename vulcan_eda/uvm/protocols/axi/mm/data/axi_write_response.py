import dataclasses

from vulcan_eda.uvm.protocols.axi.mm.data.axi_response import AxiResponse

@dataclasses.dataclass(frozen=True)
class AxiWriteResponse:
    response: AxiResponse
    id: int = 0

    def to_values(self):
        return (self.id, self.response.value)

    @classmethod
    def from_values(cls, values):
        txn_id, response = values
        return cls(response=AxiResponse(int(response)), id=int(txn_id))
