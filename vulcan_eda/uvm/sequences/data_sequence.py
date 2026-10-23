import random

import pyuvm

from vulcan_eda.uvm.configs.sequences.random_data_sequence_config import RandomDataSequenceConfig
from vulcan_eda.uvm.sequences.transaction_sequence import TransactionSequence

class DataSequenceItem(pyuvm.uvm_sequence_item):
    def __init__(self, name, data):
        super().__init__(name)
        self.data = data

class RandomDataSequence(TransactionSequence):
    def _configure(self):
        super()._configure()
        if not (self.txn_pct == 100):
            raise ValueError("txn_pct must be 100")
        config = pyuvm.ConfigDB().get(self.sequencer, "", "random_data_sequence_config", RandomDataSequenceConfig())
        self.min_data = config.min_data
        self.max_data = config.max_data

    def _get_next_sequence_item(self, is_txn):
        data = random.randint(self.min_data, self.max_data)
        return DataSequenceItem('random_data_sequence_item', data)

class IterableDataSequence(TransactionSequence):
    iterable = ()

    def _configure(self):
        super()._configure()
        if not (self.txn_pct == 100):
            raise ValueError("txn_pct must be 100")
        data = list(self.iterable)
        if not data:
            raise ValueError("iterable must not be empty")
        self.max_num_txn = len(data) - 1
        self._iterator = iter(data)

    def _get_next_sequence_item(self, is_txn):
        return DataSequenceItem('iterable_data_sequence_item', next(self._iterator))
