import pytest
import pyuvm

from vulcan_eda.uvm.subscribers.translation_subscriber import TranslationSubscriber

from tests.support.data import Unprintable

class ChannelTaggingTranslationSubscriber(TranslationSubscriber):
    channels = ("x", "y")
    copies = 1

    def translate(self, channel, lower_item):
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
        TranslationSubscriber.create("translation_subscriber", None).translate("x", "a")

def reported_messages(caplog, translation_subscriber, lower_items):
    translation_subscriber.logger.addHandler(caplog.handler)
    try:
        for lower_item in lower_items:
            translation_subscriber.analysis_exports["x"].write(lower_item)
        translation_subscriber.report_phase()
    finally:
        translation_subscriber.logger.removeHandler(caplog.handler)
    return [record.getMessage() for record in caplog.records]

def test_reports_a_summary_of_translated_items(caplog, recording_subscriber):
    translation_subscriber = build(recording_subscriber, copies=2)
    assert reported_messages(caplog, translation_subscriber, ["a"]) == ["[SUMMARY] translated 2 item(s)"]

def test_reports_translated_items_at_high_verbosity(caplog, recording_subscriber):
    translation_subscriber = build(recording_subscriber, copies=1)
    translation_subscriber.set_report_verbosity(pyuvm.UVM_HIGH)
    assert reported_messages(caplog, translation_subscriber, ["a", "b"]) == ["[TRANSLATED] translated ('x', 'a')", "[TRANSLATED] translated ('x', 'b')", "[SUMMARY] translated 2 item(s)"]

def test_formats_no_translated_item_below_high_verbosity(recording_subscriber):
    unprintable = Unprintable()
    build(recording_subscriber, copies=1).analysis_exports["x"].write(unprintable)
    assert recording_subscriber.items == [("x", unprintable)]
