import dataclasses

from vulcan_eda.uvm.protocols.axi.mm.data.axi_response import AxiResponse

@dataclasses.dataclass(frozen=True)
class AxiReadData:
    data: int
    response: AxiResponse
    last: bool = True
    id: int = 0

    def to_values(self):
        return (self.id, self.data, self.response.value, self.last)

    @classmethod
    def from_values(cls, values):
        txn_id, data, response, last = values
        return cls(data=int(data), response=AxiResponse(int(response)), last=bool(last), id=int(txn_id))
