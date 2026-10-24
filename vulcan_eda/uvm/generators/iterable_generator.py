import dataclasses
import typing

@dataclasses.dataclass(frozen=True)
class IterableGenerator:
    values: tuple[typing.Any, ...]

    def __post_init__(self):
        object.__setattr__(self, "values", tuple(self.values))

    def __iter__(self):
        return iter(self.values)
