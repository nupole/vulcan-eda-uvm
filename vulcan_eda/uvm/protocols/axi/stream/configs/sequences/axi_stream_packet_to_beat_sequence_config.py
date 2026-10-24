import dataclasses
import typing

from vulcan_eda.uvm.configs.generator_config import GeneratorConfig
from vulcan_eda.uvm.generators.constant_generator import ConstantGenerator

@dataclasses.dataclass(frozen=True)
class AxiStreamPacketToBeatSequenceConfig(GeneratorConfig):
    valid_generator: typing.Iterable = ConstantGenerator(True)
