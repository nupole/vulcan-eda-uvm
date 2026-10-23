import asyncio
import collections

import pytest

from vulcan_eda.uvm.sequences.translation_sequence import TranslationSequence

class Drained(Exception):
    pass

class UpperSequencer:
    def __init__(self, items, log):
        self._items = collections.deque(items)
        self._log = log
        self.seq_item_export = self

    async def get_next_item(self):
        if not self._items:
            raise Drained()
        self._current_item = self._items.popleft()
        return self._current_item

    def item_done(self):
        self._log.append(("item_done", self._current_item))

class RecordingTranslationSequence(TranslationSequence):
    def __init__(self, name, log):
        super().__init__(name)
        self._log = log

    async def _translate(self, upper_item):
        self._log.append(("translate", upper_item))

def run(items):
    log = []
    translation_sequence = RecordingTranslationSequence("translation_sequence", log)
    translation_sequence.upper_sequencer = UpperSequencer(items, log)
    with pytest.raises(Drained):
        asyncio.run(translation_sequence.body())
    return log

def test_translates_each_item_before_item_done():
    assert run(["a", "b"]) == [
        ("translate", "a"),
        ("item_done", "a"),
        ("translate", "b"),
        ("item_done", "b"),
    ]

def test_translate_must_be_overridden():
    translation_sequence = TranslationSequence("translation_sequence")
    with pytest.raises(NotImplementedError):
        asyncio.run(translation_sequence._translate("a"))
