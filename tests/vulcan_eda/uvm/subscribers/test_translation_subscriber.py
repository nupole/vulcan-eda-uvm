import pytest

from vulcan_eda.uvm.subscribers.translation_subscriber import TranslationSubscriber

class ChannelTaggingTranslationSubscriber(TranslationSubscriber):
    channels = ("x", "y")
    copies = 1

    def _translate(self, channel, lower_item):
        return [(channel, lower_item)] * self.copies

def build(recording_subscriber, copies):
    translation_subscriber = ChannelTaggingTranslationSubscriber.create("translation_subscriber", None)
    translation_subscriber.copies = copies
    translation_subscriber.build_phase()
    translation_subscriber.analysis_port.connect(recording_subscriber.analysis_export)
    return translation_subscriber

def test_has_an_analysis_export_per_channel(recording_subscriber):
    assert set(build(recording_subscriber, copies=1).analysis_exports) == {"x", "y"}

def test_publishes_each_translated_item_with_its_channel(recording_subscriber):
    translation_subscriber = build(recording_subscriber, copies=2)
    translation_subscriber.analysis_exports["y"].write("a")
    assert recording_subscriber.items == [("y", "a"), ("y", "a")]

def test_publishes_nothing_until_translation_completes(recording_subscriber):
    translation_subscriber = build(recording_subscriber, copies=0)
    translation_subscriber.analysis_exports["x"].write("a")
    assert recording_subscriber.items == []

def test_translate_must_be_overridden():
    with pytest.raises(NotImplementedError):
        TranslationSubscriber.create("translation_subscriber", None)._translate("x", "a")
