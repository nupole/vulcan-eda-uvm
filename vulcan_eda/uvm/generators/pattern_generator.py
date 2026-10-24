import dataclasses
import itertools
import typing

@dataclasses.dataclass(frozen=True)
class PatternGenerator:
    values: tuple[typing.Any, ...]

    def __post_init__(self):
        object.__setattr__(self, "values", tuple(self.values))
        if not self.values:
            raise ValueError("values must not be empty")

    def __iter__(self):
        return itertools.cycle(self.values)
