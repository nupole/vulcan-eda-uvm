import dataclasses

from vulcan_eda.uvm.data.formatted_data import FormattedData
from vulcan_eda.uvm.protocols.axi.mm.data.axi_burst import AxiBurst
from vulcan_eda.uvm.signals.bundle import Bundle
from vulcan_eda.uvm.signals.constant import Constant

@dataclasses.dataclass(frozen=True, kw_only=True)
class AxiAddress(FormattedData):
    address: int = dataclasses.field(metadata={"format": "#x"})
    bytes_per_beat: int
    num_beats: int = 1
    id: int = 0
    burst: AxiBurst = AxiBurst.INCR
    prot: int = 0

    def __post_init__(self):
        if not (1 <= self.num_beats <= 256):
            raise ValueError("num_beats must be between 1 and 256")
        if not (self.bytes_per_beat > 0 and self.bytes_per_beat & (self.bytes_per_beat - 1) == 0):
            raise ValueError("bytes_per_beat must be a power of two")

    @classmethod
    def signals(cls, address, bytes_per_beat, prot, id=Constant(0), num_beats=Constant(0), burst=Constant(AxiBurst.INCR.value)):
        return Bundle(id, address, num_beats, bytes_per_beat, burst, prot)

    def to_values(self):
        return (self.id, self.address, self.num_beats - 1, self.bytes_per_beat.bit_length() - 1, self.burst.value, self.prot)

    @classmethod
    def from_values(cls, values):
        txn_id, address, encoded_len, encoded_size, burst, prot = values
        return cls(
            address=int(address),
            bytes_per_beat=2 ** int(encoded_size),
            num_beats=int(encoded_len) + 1,
            id=int(txn_id),
            burst=AxiBurst(int(burst)),
            prot=int(prot))
