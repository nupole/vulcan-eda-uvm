import pytest

from vulcan_eda.uvm.configs.layers import TranslationLayerConfig
from vulcan_eda.uvm.sequences.translation_sequence import TranslationSequence

def test_requires_translation_sequence_type():
    with pytest.raises(TypeError):
        TranslationLayerConfig()

def test_forwards_nothing_by_default():
    assert TranslationLayerConfig(TranslationSequence).forwarded_configs == {}

def test_keeps_forwarded_configs():
    forwarded_configs = {"axi_stream_config": object()}
    assert TranslationLayerConfig(TranslationSequence, forwarded_configs).forwarded_configs == forwarded_configs

def test_rejects_non_translation_sequence_type():
    with pytest.raises(TypeError):
        TranslationLayerConfig(object)
