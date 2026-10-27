import dataclasses
import typing

from vulcan_eda.uvm.configs.generator_config import GeneratorConfig
from vulcan_eda.uvm.generators.constant_generator import ConstantGenerator

@dataclasses.dataclass(frozen=True)
class AxiTransactionToChannelSequenceConfig(GeneratorConfig):
    awvalid_generator: typing.Iterable = ConstantGenerator(True)
    wvalid_generator: typing.Iterable = ConstantGenerator(True)
    arvalid_generator: typing.Iterable = ConstantGenerator(True)
