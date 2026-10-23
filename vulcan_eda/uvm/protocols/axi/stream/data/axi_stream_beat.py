import dataclasses

@dataclasses.dataclass(frozen=True)
class AxiStreamBeat:
    data: int
    last: bool

    def to_values(self):
        return (self.data, self.last)

    @classmethod
    def from_values(cls, values):
        data, last = values
        return cls(int(data), bool(last))
