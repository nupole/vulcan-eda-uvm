import pytest

from vulcan_eda.uvm.subscribers.translation_subscriber import TranslationSubscriber

class CopyingTranslationSubscriber(TranslationSubscriber):
    copies = 1

    def _translate(self, lower_item):
        return [lower_item] * self.copies

def build(recording_subscriber, copies):
    translation_subscriber = CopyingTranslationSubscriber.create("translation_subscriber", None)
    translation_subscriber.copies = copies
    translation_subscriber.build_phase()
    translation_subscriber.analysis_port.connect(recording_subscriber.analysis_export)
    return translation_subscriber

def test_publishes_each_translated_item(recording_subscriber):
    translation_subscriber = build(recording_subscriber, copies=2)
    translation_subscriber.analysis_export.write("a")
    assert recording_subscriber.items == ["a", "a"]

def test_publishes_nothing_until_translation_completes(recording_subscriber):
    translation_subscriber = build(recording_subscriber, copies=0)
    translation_subscriber.analysis_export.write("a")
    assert recording_subscriber.items == []

def test_translate_must_be_overridden():
    with pytest.raises(NotImplementedError):
        TranslationSubscriber.create("translation_subscriber", None)._translate("a")
