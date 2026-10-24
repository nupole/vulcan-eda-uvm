import dataclasses

import pytest
import pyuvm

from vulcan_eda.uvm.configs import BaseConfig

@dataclasses.dataclass(frozen=True)
class StimulusConfig(BaseConfig):
    count: int = 10

@dataclasses.dataclass(frozen=True)
class ProtocolConfig(BaseConfig):
    width: int

@dataclasses.dataclass(frozen=True)
class ValidatedConfig(BaseConfig):
    count: int = 0

    def __post_init__(self):
        if not (self.count > 0):
            raise ValueError("count must be positive")

@pytest.fixture
def component():
    return pyuvm.uvm_component("component", None)

def test_get_returns_the_config_that_was_set(component):
    StimulusConfig(3).set(component)
    assert StimulusConfig.get(component) == StimulusConfig(3)

def test_set_scopes_to_a_child_path():
    parent = pyuvm.uvm_component("parent", None)
    child = pyuvm.uvm_component("child", parent)
    ProtocolConfig(8).set(parent, "child")
    assert ProtocolConfig.get(child) == ProtocolConfig(8)

def test_get_defaults_when_nothing_was_set(component):
    assert StimulusConfig.get(component) == StimulusConfig()

def test_get_fails_loudly_for_a_missing_config_without_defaults(component):
    with pytest.raises(pyuvm.UVMConfigItemNotFound, match="no ProtocolConfig set for component"):
        ProtocolConfig.get(component)

def test_get_fails_loudly_when_the_default_is_invalid(component):
    with pytest.raises(pyuvm.UVMConfigItemNotFound, match="no ValidatedConfig set"):
        ValidatedConfig.get(component)

def test_a_protocol_config_that_was_set_is_returned_without_building_a_default(component):
    ProtocolConfig(8).set(component)
    assert ProtocolConfig.get(component) == ProtocolConfig(8)

def test_configs_of_different_types_do_not_collide(component):
    StimulusConfig(3).set(component)
    ProtocolConfig(8).set(component)
    assert (StimulusConfig.get(component), ProtocolConfig.get(component)) == (StimulusConfig(3), ProtocolConfig(8))

def test_key_is_the_full_class_path():
    assert StimulusConfig.key() == f"{__name__}.StimulusConfig"

def test_get_and_set_work_at_the_root():
    StimulusConfig(3).set(None)
    assert StimulusConfig.get(None) == StimulusConfig(3)

def test_get_fails_loudly_at_the_root():
    with pytest.raises(pyuvm.UVMConfigItemNotFound, match="no ProtocolConfig set for the root"):
        ProtocolConfig.get(None)
