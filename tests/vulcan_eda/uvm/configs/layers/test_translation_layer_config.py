import pytest

from vulcan_eda.uvm.configs.layers import TranslationLayerConfig
from vulcan_eda.uvm.sequences.translation_sequence import TranslationSequence
from vulcan_eda.uvm.subscribers.translation_subscriber import TranslationSubscriber

def test_requires_a_translation_type():
    with pytest.raises(ValueError):
        TranslationLayerConfig()

@pytest.mark.parametrize("translation_types", [
    {"translation_sequence_type": TranslationSequence},
    {"translation_subscriber_type": TranslationSubscriber},
    {"translation_sequence_type": TranslationSequence, "translation_subscriber_type": TranslationSubscriber},
])
def test_accepts_either_or_both_translation_types(translation_types):
    TranslationLayerConfig(**translation_types)

def test_forwards_nothing_by_default():
    assert TranslationLayerConfig(translation_sequence_type=TranslationSequence).forwarded_configs == {}

def test_keeps_forwarded_configs():
    forwarded_configs = {"axi_stream_config": object()}
    assert TranslationLayerConfig(translation_sequence_type=TranslationSequence, forwarded_configs=forwarded_configs).forwarded_configs == forwarded_configs

def test_rejects_non_translation_sequence_type():
    with pytest.raises(TypeError):
        TranslationLayerConfig(translation_sequence_type=object)

def test_rejects_non_translation_subscriber_type():
    with pytest.raises(TypeError):
        TranslationLayerConfig(translation_subscriber_type=object)

def test_is_keyword_only():
    with pytest.raises(TypeError):
        TranslationLayerConfig(TranslationSequence)
