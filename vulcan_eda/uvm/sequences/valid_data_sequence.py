import random

import pyuvm

from vulcan_eda.uvm.sequences.random_data_sequence_config import RandomDataSequenceConfig
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
    def _configure(self):
        super()._configure()
        config = pyuvm.ConfigDB().get(self.sequencer, "", "random_data_sequence_config", RandomDataSequenceConfig())
        self.min_data = config.min_data
        self.max_data = config.max_data

    def _get_data(self):
        return self._get_random_data()

    def _get_random_data(self):
        return random.randint(self.min_data, self.max_data)
