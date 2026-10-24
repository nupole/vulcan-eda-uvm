import dataclasses
import enum
import typing

import pyuvm

from vulcan_eda.uvm.configs.base_config import BaseConfig

@dataclasses.dataclass(frozen=True, kw_only=True)
class AxiStreamEnvironmentConfig(BaseConfig):
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

    @classmethod
    def from_prefix(cls, dut, prefix, *, clk, role, is_active=pyuvm.uvm_active_passive_enum.UVM_ACTIVE):
        pins = {field.name: getattr(dut, prefix + field.name) for field in dataclasses.fields(cls) if field.name not in ("clk", "role", "is_active")}
        return cls(clk=clk, role=role, is_active=is_active, **pins)
