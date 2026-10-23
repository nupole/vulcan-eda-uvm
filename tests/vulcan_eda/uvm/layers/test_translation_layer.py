import asyncio

import pytest
import pyuvm

from vulcan_eda.uvm.configs.layers import TranslationLayerConfig
from vulcan_eda.uvm.layers import TranslationLayer
from vulcan_eda.uvm.sequences.translation_sequence import TranslationSequence
from vulcan_eda.uvm.subscribers.translation_subscriber import TranslationSubscriber

class StartRecordingTranslationSequence(TranslationSequence):
    starts = []

    async def body(self):
        StartRecordingTranslationSequence.starts.append((self.sequencer, self.upper_sequencer))

class DoublingTranslationSubscriber(TranslationSubscriber):
    def _translate(self, lower_item):
        return [lower_item, lower_item]

FORWARDED_CONFIG = object()

def build(**translation_types):
    config = TranslationLayerConfig(**translation_types, forwarded_configs={"forwarded_config": FORWARDED_CONFIG})
    pyuvm.ConfigDB().set(None, "translation_layer", "config", config)
    translation_layer = TranslationLayer.create("translation_layer", None)
    translation_layer.build_phase()
    return translation_layer

def build_stimulus():
    return build(translation_sequence_type=StartRecordingTranslationSequence)

def build_monitoring(recording_subscriber):
    translation_layer = build(translation_subscriber_type=DoublingTranslationSubscriber)
    translation_layer.subscriber.build_phase()
    translation_layer.connect_phase()
    translation_layer.analysis_port.connect(recording_subscriber.analysis_export)
    return translation_layer

def test_forwards_configs_to_its_sequencer():
    translation_layer = build_stimulus()
    assert pyuvm.ConfigDB().get(translation_layer.sequencer, "", "forwarded_config") is FORWARDED_CONFIG

def test_forwards_configs_to_lower_sequencer(recording_sequencer):
    translation_layer = build_stimulus()
    translation_layer.lower_sequencer = recording_sequencer
    translation_layer.end_of_elaboration_phase()
    assert pyuvm.ConfigDB().get(recording_sequencer, "", "forwarded_config") is FORWARDED_CONFIG

def test_requires_lower_sequencer():
    translation_layer = build_stimulus()
    with pytest.raises(pyuvm.UVMError):
        translation_layer.end_of_elaboration_phase()

def test_starts_translation_on_lower_sequencer(recording_sequencer):
    StartRecordingTranslationSequence.starts = []
    translation_layer = build_stimulus()
    translation_layer.lower_sequencer = recording_sequencer
    asyncio.run(translation_layer.run_phase())
    assert StartRecordingTranslationSequence.starts == [(recording_sequencer, translation_layer.sequencer)]

def test_translation_sequence_can_be_overridden(recording_sequencer):
    StartRecordingTranslationSequence.starts = []
    pyuvm.uvm_factory().set_type_override_by_type(TranslationSequence, StartRecordingTranslationSequence)
    translation_layer = build(translation_sequence_type=TranslationSequence)
    translation_layer.lower_sequencer = recording_sequencer
    asyncio.run(translation_layer.run_phase())
    assert len(StartRecordingTranslationSequence.starts) == 1

def test_forwards_configs_to_its_subscriber(recording_subscriber):
    translation_layer = build_monitoring(recording_subscriber)
    assert pyuvm.ConfigDB().get(translation_layer.subscriber, "", "forwarded_config") is FORWARDED_CONFIG

def test_publishes_translated_items(recording_subscriber):
    translation_layer = build_monitoring(recording_subscriber)
    translation_layer.analysis_export.write("a")
    assert recording_subscriber.items == ["a", "a"]

def test_monitoring_only_needs_no_lower_sequencer(recording_subscriber):
    translation_layer = build_monitoring(recording_subscriber)
    translation_layer.end_of_elaboration_phase()
    asyncio.run(translation_layer.run_phase())
