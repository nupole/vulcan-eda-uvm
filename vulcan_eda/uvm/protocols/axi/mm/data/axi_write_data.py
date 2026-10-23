import dataclasses

@dataclasses.dataclass(frozen=True)
class AxiWriteData:
    data: int
    strobe: int
    last: bool = True

    def to_values(self):
        return (self.data, self.strobe, self.last)

    @classmethod
    def from_values(cls, values):
        data, strobe, last = values
        return cls(data=int(data), strobe=int(strobe), last=bool(last))
