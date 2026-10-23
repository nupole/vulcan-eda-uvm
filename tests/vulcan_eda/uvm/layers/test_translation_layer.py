import asyncio

import pytest
import pyuvm

from vulcan_eda.uvm.configs.layers import TranslationLayerConfig
from vulcan_eda.uvm.layers import TranslationLayer
from vulcan_eda.uvm.sequences.translation_sequence import TranslationSequence

class StartRecordingTranslationSequence(TranslationSequence):
    starts = []

    async def body(self):
        StartRecordingTranslationSequence.starts.append((self.sequencer, self.upper_sequencer))

FORWARDED_CONFIG = object()

def build(translation_sequence_type=StartRecordingTranslationSequence):
    config = TranslationLayerConfig(translation_sequence_type, {"forwarded_config": FORWARDED_CONFIG})
    pyuvm.ConfigDB().set(None, "translation_layer", "config", config)
    translation_layer = TranslationLayer.create("translation_layer", None)
    translation_layer.build_phase()
    return translation_layer

def test_forwards_configs_to_its_sequencer():
    translation_layer = build()
    assert pyuvm.ConfigDB().get(translation_layer.sequencer, "", "forwarded_config") is FORWARDED_CONFIG

def test_forwards_configs_to_lower_sequencer(recording_sequencer):
    translation_layer = build()
    translation_layer.lower_sequencer = recording_sequencer
    translation_layer.end_of_elaboration_phase()
    assert pyuvm.ConfigDB().get(recording_sequencer, "", "forwarded_config") is FORWARDED_CONFIG

def test_requires_lower_sequencer():
    translation_layer = build()
    with pytest.raises(pyuvm.UVMError):
        translation_layer.end_of_elaboration_phase()

def test_starts_translation_on_lower_sequencer(recording_sequencer):
    StartRecordingTranslationSequence.starts = []
    translation_layer = build()
    translation_layer.lower_sequencer = recording_sequencer
    asyncio.run(translation_layer.run_phase())
    assert StartRecordingTranslationSequence.starts == [(recording_sequencer, translation_layer.sequencer)]

def test_translation_sequence_can_be_overridden(recording_sequencer):
    StartRecordingTranslationSequence.starts = []
    pyuvm.uvm_factory().set_type_override_by_type(TranslationSequence, StartRecordingTranslationSequence)
    translation_layer = build(TranslationSequence)
    translation_layer.lower_sequencer = recording_sequencer
    asyncio.run(translation_layer.run_phase())
    assert len(StartRecordingTranslationSequence.starts) == 1
