import types

import pytest
import pyuvm

from vulcan_eda.uvm.generators import ConstantGenerator, PatternGenerator
from vulcan_eda.uvm.protocols.axi.mm.configs import AxiConfig
from vulcan_eda.uvm.protocols.axi.mm.configs.environments import AxiEnvironmentConfig

LITE_PINS = (
    "awaddr", "awprot", "awvalid", "awready",
    "wdata", "wstrb", "wvalid", "wready",
    "bresp", "bvalid", "bready",
    "araddr", "arprot", "arvalid", "arready",
    "rdata", "rresp", "rvalid", "rready")

def dut(prefix, pins):
    return types.SimpleNamespace(**{prefix + pin: f"{prefix}{pin} handle" for pin in pins})

def test_from_prefix_finds_lite_pins():
    config = AxiEnvironmentConfig.from_prefix(dut("s_axi_", LITE_PINS), "s_axi_", clk="clk", profile=AxiConfig.Profile.LITE)
    assert all(getattr(config, pin) == f"s_axi_{pin} handle" for pin in LITE_PINS)

def test_from_prefix_leaves_missing_optional_pins_unset():
    config = AxiEnvironmentConfig.from_prefix(dut("s_axi_", LITE_PINS), "s_axi_", clk="clk", profile=AxiConfig.Profile.LITE)
    assert (config.awid, config.awlen, config.wlast, config.rlast) == (None, None, None, None)

def test_from_prefix_finds_present_optional_pins():
    config = AxiEnvironmentConfig.from_prefix(dut("", LITE_PINS + ("awlen", "rlast")), "", clk="clk", profile=AxiConfig.Profile.LITE)
    assert (config.awlen, config.rlast) == ("awlen handle", "rlast handle")

def test_from_prefix_rejects_missing_required_pin():
    with pytest.raises(AttributeError, match="s_axi_wstrb"):
        AxiEnvironmentConfig.from_prefix(dut("s_axi_", [pin for pin in LITE_PINS if pin != "wstrb"]), "s_axi_", clk="clk", profile=AxiConfig.Profile.LITE)

def test_from_prefix_defaults_to_active():
    config = AxiEnvironmentConfig.from_prefix(dut("", LITE_PINS), "", clk="clk", profile=AxiConfig.Profile.LITE)
    assert config.is_active is pyuvm.uvm_active_passive_enum.UVM_ACTIVE

def test_from_prefix_can_be_passive():
    config = AxiEnvironmentConfig.from_prefix(dut("", LITE_PINS), "", clk="clk", profile=AxiConfig.Profile.LITE, is_active=pyuvm.uvm_active_passive_enum.UVM_PASSIVE)
    assert config.is_active is pyuvm.uvm_active_passive_enum.UVM_PASSIVE

def test_explicit_pins_require_lite_pins():
    pins = {pin: f"{pin} handle" for pin in LITE_PINS if pin != "rready"}
    with pytest.raises(TypeError):
        AxiEnvironmentConfig(clk="clk", profile=AxiConfig.Profile.LITE, **pins)

@pytest.mark.parametrize("field", ["bready_generator", "rready_generator"])
def test_is_always_ready_by_default(field):
    config = AxiEnvironmentConfig.from_prefix(dut("", LITE_PINS), "", clk="clk", profile=AxiConfig.Profile.LITE)
    assert getattr(config, field) == ConstantGenerator(True)

@pytest.mark.parametrize("field", ["bready_generator", "rready_generator"])
def test_from_prefix_takes_a_ready_generator_instead_of_a_pin(field):
    config = AxiEnvironmentConfig.from_prefix(dut("", LITE_PINS + (field,)), "", clk="clk", profile=AxiConfig.Profile.LITE, **{field: PatternGenerator((0, 1))})
    assert getattr(config, field) == PatternGenerator((0, 1))

@pytest.mark.parametrize("field", ["bready_generator", "rready_generator"])
def test_rejects_a_one_shot_ready_generator(field):
    with pytest.raises(TypeError, match=f"{field} must be re-iterable"):
        AxiEnvironmentConfig.from_prefix(dut("", LITE_PINS), "", clk="clk", profile=AxiConfig.Profile.LITE, **{field: iter((0, 1))})
