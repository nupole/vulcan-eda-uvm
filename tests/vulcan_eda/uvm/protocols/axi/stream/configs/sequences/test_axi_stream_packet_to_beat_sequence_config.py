import dataclasses

import pytest

from vulcan_eda.uvm.generators import ConstantGenerator, PatternGenerator, RandomBooleanGenerator
from vulcan_eda.uvm.protocols.axi.stream.configs.sequences import AxiStreamPacketToBeatSequenceConfig

def test_defaults_to_always_valid():
    assert AxiStreamPacketToBeatSequenceConfig().valid_generator == ConstantGenerator(True)

@pytest.mark.parametrize("valid_generator", [RandomBooleanGenerator(50), PatternGenerator((1, 0)), (True, False)])
def test_accepts_immutable_re_iterable_valid_generators(valid_generator):
    assert AxiStreamPacketToBeatSequenceConfig(valid_generator).valid_generator is valid_generator

@pytest.mark.parametrize("valid_generator", [iter((True, False)), (valid for valid in (True, False))])
def test_rejects_one_shot_iterators(valid_generator):
    with pytest.raises(TypeError, match="re-iterable"):
        AxiStreamPacketToBeatSequenceConfig(valid_generator)

@pytest.mark.parametrize("valid_generator", [[True, False], (True, [False])])
def test_rejects_mutable_valid_generators(valid_generator):
    with pytest.raises(TypeError, match="immutable"):
        AxiStreamPacketToBeatSequenceConfig(valid_generator)

def test_rejects_valid_generators_that_are_not_iterable():
    with pytest.raises(TypeError):
        AxiStreamPacketToBeatSequenceConfig(5)

def test_is_frozen():
    with pytest.raises(dataclasses.FrozenInstanceError):
        AxiStreamPacketToBeatSequenceConfig().valid_generator = (True,)
