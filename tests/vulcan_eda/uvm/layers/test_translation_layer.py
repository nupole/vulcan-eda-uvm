import asyncio
import dataclasses

import pytest
import pyuvm

from vulcan_eda.uvm.configs import BaseConfig
from vulcan_eda.uvm.configs.layers import TranslationLayerConfig
from vulcan_eda.uvm.layers import TranslationLayer
from vulcan_eda.uvm.sequences.translation_sequence import TranslationSequence
from vulcan_eda.uvm.subscribers.translation_subscriber import TranslationSubscriber

class StartRecordingTranslationSequence(TranslationSequence):
    channels = ("lower",)
    starts = []

    async def body(self):
        StartRecordingTranslationSequence.starts.append((self.upper_sequencer, self.lower_sequencers, self.responses))

class ResponseUsingTranslationSequence(StartRecordingTranslationSequence):
    uses_responses = True

class DoublingTranslationSubscriber(TranslationSubscriber):
    channels = ("lower",)

    def _translate(self, channel, lower_item):
        return [lower_item, lower_item]

@dataclasses.dataclass(frozen=True)
class ForwardedConfig(BaseConfig):
    value: int

FORWARDED_CONFIG = ForwardedConfig(1)

def build(**translation_types):
    TranslationLayerConfig(**translation_types, forwarded_configs=(FORWARDED_CONFIG,)).set(None, "translation_layer")
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
    assert ForwardedConfig.get(translation_layer.sequencer) is FORWARDED_CONFIG

def test_forwards_configs_to_lower_sequencers(recording_sequencer):
    translation_layer = build_stimulus()
    translation_layer.lower_sequencers["lower"] = recording_sequencer
    translation_layer.end_of_elaboration_phase()
    assert ForwardedConfig.get(recording_sequencer) is FORWARDED_CONFIG

def test_requires_a_lower_sequencer_per_channel():
    translation_layer = build_stimulus()
    with pytest.raises(pyuvm.UVMError):
        translation_layer.end_of_elaboration_phase()

def test_rejects_unknown_lower_channels(recording_sequencer):
    translation_layer = build_stimulus()
    translation_layer.lower_sequencers["lower"] = recording_sequencer
    translation_layer.lower_sequencers["typo"] = recording_sequencer
    with pytest.raises(pyuvm.UVMError):
        translation_layer.end_of_elaboration_phase()

def test_starts_translation_with_its_sequencers(recording_sequencer):
    StartRecordingTranslationSequence.starts = []
    translation_layer = build_stimulus()
    translation_layer.lower_sequencers["lower"] = recording_sequencer
    asyncio.run(translation_layer.run_phase())
    assert StartRecordingTranslationSequence.starts == [(translation_layer.sequencer, {"lower": recording_sequencer}, None)]

def test_translation_sequence_can_be_overridden():
    StartRecordingTranslationSequence.starts = []
    pyuvm.uvm_factory().set_type_override_by_type(TranslationSequence, StartRecordingTranslationSequence)
    translation_layer = build(translation_sequence_type=TranslationSequence)
    asyncio.run(translation_layer.run_phase())
    assert len(StartRecordingTranslationSequence.starts) == 1

def test_forwards_configs_to_its_subscriber(recording_subscriber):
    translation_layer = build_monitoring(recording_subscriber)
    assert ForwardedConfig.get(translation_layer.subscriber) is FORWARDED_CONFIG

def test_publishes_translated_items(recording_subscriber):
    translation_layer = build_monitoring(recording_subscriber)
    translation_layer.analysis_exports["lower"].write("a")
    assert recording_subscriber.items == ["a", "a"]

def build_both_directions(translation_sequence_type=ResponseUsingTranslationSequence):
    translation_layer = build(translation_sequence_type=translation_sequence_type, translation_subscriber_type=DoublingTranslationSubscriber)
    translation_layer.subscriber.build_phase()
    translation_layer.connect_phase()
    return translation_layer

def test_collects_translated_items_as_responses():
    translation_layer = build_both_directions()
    translation_layer.analysis_exports["lower"].write("a")
    assert translation_layer.responses.used() == 2

def test_has_no_responses_when_translation_does_not_use_them():
    assert build_both_directions(StartRecordingTranslationSequence).responses is None

def test_hands_responses_to_translation_sequence(recording_sequencer):
    StartRecordingTranslationSequence.starts = []
    translation_layer = build_both_directions()
    translation_layer.lower_sequencers["lower"] = recording_sequencer
    asyncio.run(translation_layer.run_phase())
    assert StartRecordingTranslationSequence.starts[0][2] is translation_layer.responses

def test_monitoring_only_needs_no_lower_sequencers(recording_subscriber):
    translation_layer = build_monitoring(recording_subscriber)
    translation_layer.end_of_elaboration_phase()
    asyncio.run(translation_layer.run_phase())
