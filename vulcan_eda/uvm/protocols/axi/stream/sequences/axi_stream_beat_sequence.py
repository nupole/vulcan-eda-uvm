import collections

from vulcan_eda.uvm.sequences.transaction_sequence import TransactionSequence
from vulcan_eda.uvm.sequences.valid_data_sequence import ValidDataSequenceItem

class AxiStreamBeatSequence(TransactionSequence):
    def __init__(self, name):
        super().__init__(name)
        self.beats = []

    def _configure(self):
        super()._configure()
        self._beats = collections.deque(self.beats)
        self.max_num_txn = len(self._beats)

    def _get_next_sequence_item(self, is_txn):
        beat = self._beats.popleft() if is_txn else None
        return ValidDataSequenceItem('axi_stream_beat_sequence_item', is_txn, beat)
