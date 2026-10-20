import random

import pyuvm

from vulcan_eda.uvm.sequences.transaction_sequence import TransactionSequence

class ValidDataSequenceItem(pyuvm.uvm_sequence_item):
    def __init__(self, name, valid, data):
        super().__init__(name)
        self.valid = valid
        self.data = data

class ValidDataSequence(TransactionSequence):
    def _get_next_sequence_item(self, is_txn):
        if is_txn:
            data = self._get_data()
        else:
            data = self._get_random_data()
        return ValidDataSequenceItem('valid_data_sequence_item', is_txn, data)

class RandomValidDataSequence(ValidDataSequence):
    @property
    def max_data(self):
        return self._max_data

    @max_data.setter
    def max_data(self, value):
        if value < 0:
            raise ValueError("max_data must be positive")
        self._max_data = value

    def _get_data(self):
        return self._get_random_data()

    def _get_random_data(self):
        self._max_data = pyuvm.ConfigDB().get(self.sequencer, "", "max_data", 255)
        return random.randint(0, self._max_data)
