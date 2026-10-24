import dataclasses
import typing

from vulcan_eda.uvm.generators.constant_generator import ConstantGenerator

@dataclasses.dataclass(frozen=True)
class AxiStreamPacketToBeatSequenceConfig:
    valid_generator: typing.Iterable = ConstantGenerator(True)

    def __post_init__(self):
        if iter(self.valid_generator) is self.valid_generator:
            raise TypeError("valid_generator must be re-iterable, not a one-shot iterator; use a generator such as PatternGenerator")
        try:
            hash(self.valid_generator)
        except TypeError:
            raise TypeError("valid_generator must be immutable; use a tuple or a generator instead of a list") from None
