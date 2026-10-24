import dataclasses

from vulcan_eda.uvm.protocols.axi.stream.data.axi_stream_beat import AxiStreamBeat

@dataclasses.dataclass(frozen=True)
class AxiStreamPacket:
    data: bytes

    def to_beats(self, num_bytes):
        if len(self.data) == 0 or len(self.data) % num_bytes != 0:
            raise ValueError("packet length must be a non-zero multiple of num_bytes")
        beats = []
        for offset in range(0, len(self.data), num_bytes):
            data = int.from_bytes(self.data[offset:offset + num_bytes], "little")
            last = offset + num_bytes == len(self.data)
            beats.append(AxiStreamBeat(data=data, last=last))
        return beats

    @classmethod
    def from_beats(cls, beats, num_bytes):
        if len(beats) == 0:
            raise ValueError("packet must have at least one beat")
        *leading_beats, final_beat = beats
        if not final_beat.last:
            raise ValueError("last must be set on the final beat")
        if any(beat.last for beat in leading_beats):
            raise ValueError("last must only be set on the final beat")
        data = bytes()
        for beat in beats:
            data += beat.data.to_bytes(num_bytes, "little")
        return cls(data)
