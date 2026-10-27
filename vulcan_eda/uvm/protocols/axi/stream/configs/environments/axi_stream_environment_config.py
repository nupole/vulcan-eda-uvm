import dataclasses
import enum
import typing

import pyuvm

from vulcan_eda.uvm.configs.generator_config import GeneratorConfig
from vulcan_eda.uvm.generators.constant_generator import ConstantGenerator

@dataclasses.dataclass(frozen=True, kw_only=True)
class AxiStreamEnvironmentConfig(GeneratorConfig):
    class Role(enum.Enum):
        TRANSMITTER = enum.auto()
        RECEIVER = enum.auto()

    clk: typing.Any
    role: Role
    is_active: pyuvm.uvm_active_passive_enum = pyuvm.uvm_active_passive_enum.UVM_ACTIVE
    tready: typing.Any
    tvalid: typing.Any
    tdata: typing.Any
    tlast: typing.Any
    ready_generator: typing.Iterable = ConstantGenerator(1)

    @classmethod
    def from_prefix(cls, dut, prefix, *, clk, role, **settings):
        pins = {field.name: getattr(dut, prefix + field.name) for field in dataclasses.fields(cls) if field.name not in ("clk", "role", "is_active", "ready_generator")}
        return cls(clk=clk, role=role, **settings, **pins)
