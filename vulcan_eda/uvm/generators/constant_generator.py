import dataclasses
import itertools
import typing

@dataclasses.dataclass(frozen=True)
class ConstantGenerator:
    value: typing.Any

    def __iter__(self):
        return itertools.repeat(self.value)
