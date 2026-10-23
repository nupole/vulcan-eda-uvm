import asyncio

import pytest
import pyuvm

from vulcan_eda.uvm.configs.sequences.transaction_sequence_config import TransactionSequenceConfig
from vulcan_eda.uvm.protocols.axi.stream.configs import AxiStreamConfig
from vulcan_eda.uvm.protocols.axi.stream.data.axi_stream_beat import AxiStreamBeat
from vulcan_eda.uvm.protocols.axi.stream.sequences.axi_stream_beat_sequence import AxiStreamBeatSequence

class RecordingSequencer(pyuvm.uvm_sequencer):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.items = []

    async def start_item(self, item):
        pass

    async def finish_item(self, item):
        self.items.append(item)

@pytest.fixture
def sequencer():
    sequencer = RecordingSequencer("sequencer", None)
    pyuvm.ConfigDB().set(sequencer, "", "axi_stream_config", AxiStreamConfig(num_bytes=4))
    return sequencer

def run(sequencer, beats):
    axi_stream_beat_sequence = AxiStreamBeatSequence.create("axi_stream_beat_sequence")
    axi_stream_beat_sequence.beats = beats
    asyncio.run(axi_stream_beat_sequence.start(sequencer))
    valid_beats = [item.data for item in sequencer.items if item.valid]
    idle_beats = [item.data for item in sequencer.items if not item.valid]
    return valid_beats, idle_beats

BEATS = [AxiStreamBeat(beat, beat == 63) for beat in range(64)]

def test_sends_beats_in_order(sequencer):
    valid_beats, _ = run(sequencer, BEATS)
    assert valid_beats == BEATS

def test_restart_sends_beats_again(sequencer):
    axi_stream_beat_sequence = AxiStreamBeatSequence.create("axi_stream_beat_sequence")
    axi_stream_beat_sequence.beats = BEATS
    asyncio.run(axi_stream_beat_sequence.start(sequencer))
    asyncio.run(axi_stream_beat_sequence.start(sequencer))
    assert [item.data for item in sequencer.items if item.valid] == BEATS + BEATS

def test_ends_with_idle(sequencer):
    run(sequencer, BEATS)
    assert not sequencer.items[-1].valid

def test_inserts_idles_between_beats_in_order(sequencer):
    pyuvm.ConfigDB().set(sequencer, "", "transaction_sequence_config", TransactionSequenceConfig(txn_pct=50))
    valid_beats, idle_beats = run(sequencer, BEATS)
    assert valid_beats == BEATS
    assert len(idle_beats) > 1

def test_idle_beats_randomize_last(sequencer):
    pyuvm.ConfigDB().set(sequencer, "", "transaction_sequence_config", TransactionSequenceConfig(txn_pct=50))
    _, idle_beats = run(sequencer, BEATS)
    assert {beat.last for beat in idle_beats} == {False, True}

def test_idle_beats_fit_tdata(sequencer):
    pyuvm.ConfigDB().set(sequencer, "", "transaction_sequence_config", TransactionSequenceConfig(txn_pct=50))
    pyuvm.ConfigDB().set(sequencer, "", "axi_stream_config", AxiStreamConfig(num_bytes=1))
    _, idle_beats = run(sequencer, BEATS)
    assert all(beat.data < 2 ** 8 for beat in idle_beats)
