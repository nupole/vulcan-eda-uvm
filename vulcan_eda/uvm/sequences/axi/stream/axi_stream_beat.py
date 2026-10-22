import dataclasses

@dataclasses.dataclass(frozen=True)
class AxiStreamBeat:
    data: int
    last: bool
