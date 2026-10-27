import asyncio

import pytest
import pyuvm

from vulcan_eda.uvm.sequences.data_sequence_item import DataSequenceItem
from vulcan_eda.uvm.sequences.translation_sequence import TranslationSequence

from tests.support.data import Unprintable

class RecordingTranslationSequence(TranslationSequence):
    def __init__(self, name):
        super().__init__(name)
        self.translations = []

    async def translate(self, upper_item):
        self.translations.append((upper_item.data, [done_item.data for done_item in self.upper_sequencer.done_items]))

class RespondingTranslationSequence(TranslationSequence):
    async def translate(self, upper_item):
        return f"response to {upper_item.data}"

class UnprintableResponseTranslationSequence(TranslationSequence):
    async def translate(self, upper_item):
        return Unprintable()

def run(translation_sequence, upper_sequencer, items):
    upper_sequencer.items.extend(items)
    translation_sequence.upper_sequencer = upper_sequencer
    with pytest.raises(upper_sequencer.Drained):
        asyncio.run(translation_sequence.body())

def test_translates_each_item_before_item_done(upper_sequencer):
    translation_sequence = RecordingTranslationSequence("translation_sequence")
    requests = [DataSequenceItem("request", "a"), DataSequenceItem("request", "b")]
    run(translation_sequence, upper_sequencer, requests)
    assert translation_sequence.translations == [("a", []), ("b", ["a"])]
    assert upper_sequencer.done_items == requests

def test_sends_no_response_when_translation_returns_none(upper_sequencer):
    run(RecordingTranslationSequence("translation_sequence"), upper_sequencer, [DataSequenceItem("request", "a")])
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

def reported_messages(caplog, translation_sequence, upper_sequencer, items):
    upper_sequencer.set_report_verbosity(pyuvm.UVM_HIGH)
    upper_sequencer.logger.addHandler(caplog.handler)
    try:
        run(translation_sequence, upper_sequencer, items)
    finally:
        upper_sequencer.logger.removeHandler(caplog.handler)
    return [record.getMessage() for record in caplog.records]

def test_reports_translated_items_through_the_upper_sequencer(caplog, upper_sequencer):
    messages = reported_messages(caplog, RecordingTranslationSequence("translation_sequence"), upper_sequencer, [DataSequenceItem("request", "a")])
    assert messages == ["[TRANSLATED] translated a"]

def test_reports_responses_with_their_translated_items(caplog, upper_sequencer):
    messages = reported_messages(caplog, RespondingTranslationSequence("translation_sequence"), upper_sequencer, [DataSequenceItem("request", "a")])
    assert messages == ["[TRANSLATED] translated a, responded response to a"]

def test_formats_no_translated_item_below_high_verbosity(upper_sequencer):
    run(RecordingTranslationSequence("translation_sequence"), upper_sequencer, [DataSequenceItem("request", Unprintable())])
    assert len(upper_sequencer.done_items) == 1

def test_formats_no_response_below_high_verbosity(upper_sequencer):
    run(UnprintableResponseTranslationSequence("translation_sequence"), upper_sequencer, [DataSequenceItem("request", Unprintable())])
    assert len(upper_sequencer.responses) == 1
