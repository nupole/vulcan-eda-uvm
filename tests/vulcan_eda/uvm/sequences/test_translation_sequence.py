import asyncio

import pytest

from vulcan_eda.uvm.sequences.data_sequence import DataSequenceItem
from vulcan_eda.uvm.sequences.translation_sequence import TranslationSequence

class RecordingTranslationSequence(TranslationSequence):
    def __init__(self, name):
        super().__init__(name)
        self.translations = []

    async def translate(self, upper_item):
        self.translations.append((upper_item, list(self.upper_sequencer.done_items)))

class RespondingTranslationSequence(TranslationSequence):
    async def translate(self, upper_item):
        return f"response to {upper_item.data}"

def run(translation_sequence, upper_sequencer, items):
    upper_sequencer.items.extend(items)
    translation_sequence.upper_sequencer = upper_sequencer
    with pytest.raises(upper_sequencer.Drained):
        asyncio.run(translation_sequence.body())

def test_translates_each_item_before_item_done(upper_sequencer):
    translation_sequence = RecordingTranslationSequence("translation_sequence")
    run(translation_sequence, upper_sequencer, ["a", "b"])
    assert translation_sequence.translations == [("a", []), ("b", ["a"])]
    assert upper_sequencer.done_items == ["a", "b"]

def test_sends_no_response_when_translation_returns_none(upper_sequencer):
    run(RecordingTranslationSequence("translation_sequence"), upper_sequencer, ["a"])
    assert upper_sequencer.responses == []

def test_sends_each_response_matched_to_its_request(upper_sequencer):
    requests = [DataSequenceItem("request", "a"), DataSequenceItem("request", "b")]
    run(RespondingTranslationSequence("translation_sequence"), upper_sequencer, requests)
    assert [(response.data, response.transaction_id) for response in upper_sequencer.responses] == [
        ("response to a", requests[0].transaction_id),
        ("response to b", requests[1].transaction_id),
    ]

def test_translate_must_be_overridden():
    translation_sequence = TranslationSequence("translation_sequence")
    with pytest.raises(NotImplementedError):
        asyncio.run(translation_sequence.translate("a"))
