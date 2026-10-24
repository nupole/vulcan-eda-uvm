import dataclasses
import itertools

@dataclasses.dataclass(frozen=True)
class IncrementingGenerator:
    start: int = 0
    step: int = 1
    width: int | None = None

    def __post_init__(self):
        if self.width is not None and not (self.width > 0):
            raise ValueError("width must be positive")
        if self.width is not None and not (0 <= self.start < 2 ** self.width):
            raise ValueError("start must fit in width bits")

    def __iter__(self):
        values = itertools.count(self.start, self.step)
        if self.width is None:
            return values
        return (value % 2 ** self.width for value in values)
