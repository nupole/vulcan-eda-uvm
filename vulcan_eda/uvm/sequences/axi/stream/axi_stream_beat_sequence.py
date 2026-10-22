import collections
import random

import pyuvm

from vulcan_eda.uvm.sequences.axi.stream.axi_stream_beat import AxiStreamBeat
from vulcan_eda.uvm.sequences.transaction_sequence import TransactionSequence
from vulcan_eda.uvm.sequences.valid_data_sequence import ValidDataSequenceItem

class AxiStreamBeatSequence(TransactionSequence):
    def __init__(self, name, beats):
        super().__init__(name)
        self._beats = collections.deque(beats)

    def _configure(self):
        super()._configure()
        self.max_num_txn = len(self._beats)
        config = pyuvm.ConfigDB().get(self.sequencer, "", "axi_stream_config")
        self._num_bytes = config.num_bytes

    def _get_next_sequence_item(self, is_txn):
        if is_txn:
            beat = self._beats.popleft()
        else:
            beat = self._get_idle_beat()
        return ValidDataSequenceItem('axi_stream_beat_sequence_item', is_txn, beat)

    def _get_idle_beat(self):
        data = random.getrandbits(8 * self._num_bytes)
        last = random.choice([False, True])
        return AxiStreamBeat(data, last)
