import dataclasses
import typing

import pytest

from vulcan_eda.uvm.configs import GeneratorConfig
from vulcan_eda.uvm.generators import ConstantGenerator, PatternGenerator

@dataclasses.dataclass(frozen=True)
class ChannelConfig(GeneratorConfig):
    valid_generator: typing.Iterable = ConstantGenerator(True)
    ready_generator: typing.Iterable = ConstantGenerator(True)
    names: list = dataclasses.field(default_factory=list)

def test_accepts_immutable_re_iterable_generators():
    assert ChannelConfig(PatternGenerator((1, 0)), (True, False)).ready_generator == (True, False)

@pytest.mark.parametrize("field", ["valid_generator", "ready_generator"])
def test_rejects_one_shot_iterators_by_field_name(field):
    with pytest.raises(TypeError, match=f"{field} must be re-iterable"):
        ChannelConfig(**{field: iter((True,))})

@pytest.mark.parametrize("field", ["valid_generator", "ready_generator"])
def test_rejects_mutable_generators_by_field_name(field):
    with pytest.raises(TypeError, match=f"{field} must be immutable"):
        ChannelConfig(**{field: [True]})

def test_ignores_fields_that_are_not_generators():
    assert ChannelConfig(names=["mutable", "is", "fine"]).names == ["mutable", "is", "fine"]
