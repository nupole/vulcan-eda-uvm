import asyncio

import pytest

from vulcan_eda.uvm.sequences.translation_sequence import TranslationSequence

class RecordingTranslationSequence(TranslationSequence):
    def __init__(self, name):
        super().__init__(name)
        self.translations = []

    async def _translate(self, upper_item):
        self.translations.append((upper_item, list(self.upper_sequencer.done_items)))

def test_translates_each_item_before_item_done(upper_sequencer):
    upper_sequencer.items.extend(["a", "b"])
    translation_sequence = RecordingTranslationSequence("translation_sequence")
    translation_sequence.upper_sequencer = upper_sequencer
    with pytest.raises(upper_sequencer.Drained):
        asyncio.run(translation_sequence.body())
    assert translation_sequence.translations == [("a", []), ("b", ["a"])]
    assert upper_sequencer.done_items == ["a", "b"]

def test_translate_must_be_overridden():
    translation_sequence = TranslationSequence("translation_sequence")
    with pytest.raises(NotImplementedError):
        asyncio.run(translation_sequence._translate("a"))
