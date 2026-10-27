import types

import pytest
import pyuvm

from vulcan_eda.uvm.configs import BaseConfig
from vulcan_eda.uvm.generators import ConstantGenerator, PatternGenerator
from vulcan_eda.uvm.protocols.axi.stream.configs.environments import AxiStreamEnvironmentConfig

PINS = ("tready", "tvalid", "tdata", "tlast")

def dut(prefix, pins):
    return types.SimpleNamespace(**{prefix + pin: f"{prefix}{pin} handle" for pin in pins})

def from_prefix(pins=PINS, **kwargs):
    return AxiStreamEnvironmentConfig.from_prefix(dut("s_axis_", pins), "s_axis_", clk="clk", role=AxiStreamEnvironmentConfig.Role.TRANSMITTER, **kwargs)

def test_is_a_base_config():
    assert isinstance(from_prefix(), BaseConfig)

def test_from_prefix_finds_every_pin():
    config = from_prefix()
    assert all(getattr(config, pin) == f"s_axis_{pin} handle" for pin in PINS)

def test_from_prefix_rejects_a_missing_pin():
    with pytest.raises(AttributeError, match="s_axis_tlast"):
        from_prefix(pins=PINS[:-1])

def test_keeps_its_role():
    config = AxiStreamEnvironmentConfig.from_prefix(dut("", PINS), "", clk="clk", role=AxiStreamEnvironmentConfig.Role.RECEIVER)
    assert config.role is AxiStreamEnvironmentConfig.Role.RECEIVER

def test_defaults_to_active():
    assert from_prefix().is_active is pyuvm.uvm_active_passive_enum.UVM_ACTIVE

def test_can_be_passive():
    assert from_prefix(is_active=pyuvm.uvm_active_passive_enum.UVM_PASSIVE).is_active is pyuvm.uvm_active_passive_enum.UVM_PASSIVE

def test_explicit_pins_are_all_required():
    with pytest.raises(TypeError):
        AxiStreamEnvironmentConfig(clk="clk", role=AxiStreamEnvironmentConfig.Role.TRANSMITTER, tready=1, tvalid=1, tdata=1)

def test_is_always_ready_by_default():
    assert from_prefix().ready_generator == ConstantGenerator(1)

def test_from_prefix_takes_a_ready_generator_instead_of_a_pin():
    assert from_prefix(ready_generator=PatternGenerator((0, 1))).ready_generator == PatternGenerator((0, 1))

def test_rejects_a_one_shot_ready_generator():
    with pytest.raises(TypeError, match="ready_generator must be re-iterable"):
        from_prefix(ready_generator=iter((0, 1)))
