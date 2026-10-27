import dataclasses

import pytest

from vulcan_eda.uvm.configs import GeneratorConfig
from vulcan_eda.uvm.generators import ConstantGenerator
from vulcan_eda.uvm.protocols.axi.mm.configs.sequences import AxiTransactionToChannelSequenceConfig

FIELDS = [field.name for field in dataclasses.fields(AxiTransactionToChannelSequenceConfig)]

def test_is_a_generator_config():
    assert isinstance(AxiTransactionToChannelSequenceConfig(), GeneratorConfig)

def test_has_a_valid_generator_for_each_channel_the_manager_sends_on():
    assert FIELDS == ["awvalid_generator", "wvalid_generator", "arvalid_generator"]

@pytest.mark.parametrize("field", FIELDS)
def test_defaults_to_always_asserted(field):
    assert getattr(AxiTransactionToChannelSequenceConfig(), field) == ConstantGenerator(True)

@pytest.mark.parametrize("field", FIELDS)
def test_rejects_mutable_generators(field):
    with pytest.raises(TypeError, match=field):
        AxiTransactionToChannelSequenceConfig(**{field: [True]})
