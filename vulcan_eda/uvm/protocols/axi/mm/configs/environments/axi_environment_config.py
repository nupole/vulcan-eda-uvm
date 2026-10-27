import dataclasses
import typing

import pyuvm

from vulcan_eda.uvm.configs.generator_config import GeneratorConfig
from vulcan_eda.uvm.generators.constant_generator import ConstantGenerator
from vulcan_eda.uvm.protocols.axi.mm.configs.axi_config import AxiConfig

@dataclasses.dataclass(frozen=True, kw_only=True)
class AxiEnvironmentConfig(GeneratorConfig):
    clk: typing.Any
    profile: AxiConfig.Profile
    is_active: pyuvm.uvm_active_passive_enum = pyuvm.uvm_active_passive_enum.UVM_ACTIVE
    awaddr: typing.Any
    awprot: typing.Any
    awvalid: typing.Any
    awready: typing.Any
    awid: typing.Any = None
    awlen: typing.Any = None
    awsize: typing.Any = None
    awburst: typing.Any = None
    wdata: typing.Any
    wstrb: typing.Any
    wvalid: typing.Any
    wready: typing.Any
    wlast: typing.Any = None
    bresp: typing.Any
    bvalid: typing.Any
    bready: typing.Any
    bid: typing.Any = None
    araddr: typing.Any
    arprot: typing.Any
    arvalid: typing.Any
    arready: typing.Any
    arid: typing.Any = None
    arlen: typing.Any = None
    arsize: typing.Any = None
    arburst: typing.Any = None
    rdata: typing.Any
    rresp: typing.Any
    rvalid: typing.Any
    rready: typing.Any
    rid: typing.Any = None
    rlast: typing.Any = None
    bready_generator: typing.Iterable = ConstantGenerator(True)
    rready_generator: typing.Iterable = ConstantGenerator(True)

    @classmethod
    def from_prefix(cls, dut, prefix, *, clk, profile, **settings):
        pins = {}
        for field in dataclasses.fields(cls):
            if field.name in ("clk", "profile", "is_active", "bready_generator", "rready_generator"):
                continue
            if field.default is dataclasses.MISSING:
                pins[field.name] = getattr(dut, prefix + field.name)
            else:
                pins[field.name] = getattr(dut, prefix + field.name, None)
        return cls(clk=clk, profile=profile, **settings, **pins)
