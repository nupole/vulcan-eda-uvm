import random

import pyuvm

from vulcan_eda.uvm.sequences.transaction_sequence import TransactionSequence

class DataSequenceItem(pyuvm.uvm_sequence_item):
    def __init__(self, name, data):
        super().__init__(name)
        self.data = data

class RandomDataSequence(TransactionSequence):
    @TransactionSequence.txn_pct.setter
    def txn_pct(self, value):
        if not (value == 100):
            raise ValueError("txn_pct must be 100")
        self._txn_pct = value

    @property
    def max_data(self):
        return self._max_data

    @max_data.setter
    def max_data(self, value):
        if value < 0:
            raise ValueError("max_data must be positive")
        self._max_data = value

    def _get_next_sequence_item(self, is_txn):
        self.max_data = pyuvm.ConfigDB().get(self.sequencer, "", "max_data", 255)
        data = random.randint(0, self._max_data)
        return DataSequenceItem('random_data_sequence_item', data)
