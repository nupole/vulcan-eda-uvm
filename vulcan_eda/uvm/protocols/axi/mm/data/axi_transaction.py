import dataclasses
import enum

from vulcan_eda.uvm.protocols.axi.mm.data.axi_burst import AxiBurst
from vulcan_eda.uvm.protocols.axi.mm.data.axi_response import AxiResponse

@dataclasses.dataclass(frozen=True)
class AxiTransaction:
    class Access(enum.Enum):
        READ = enum.auto()
        WRITE = enum.auto()

    access: Access
    address: int
    data: tuple[int, ...] = ()
    num_beats: int = 1
    id: int = 0
    burst: AxiBurst = AxiBurst.INCR
    response: AxiResponse | None = None

    def __post_init__(self):
        if not (self.num_beats > 0):
            raise ValueError("num_beats must be positive")
        if self.access is AxiTransaction.Access.WRITE and not (len(self.data) == self.num_beats):
            raise ValueError("a write must have one data word per beat")
        if self.access is AxiTransaction.Access.READ and not (len(self.data) in (0, self.num_beats)):
            raise ValueError("a read must have no data or one data word per beat")
