import random

import pyuvm

from vulcan_eda.uvm.configs.sequences.transaction_sequence_config import TransactionSequenceConfig

class TransactionSequence(pyuvm.uvm_sequence):
    def __init__(self, name):
        super().__init__(name)

    def _configure(self):
        config = pyuvm.ConfigDB().get(self.sequencer, "", "transaction_sequence_config", TransactionSequenceConfig())
        self.txn_pct = config.txn_pct
        self.max_num_txn = config.max_num_txn

    async def body(self):
        self._configure()
        num_txn = 0
        while num_txn < self.max_num_txn:
            is_txn = random.randint(1, 100) <= self.txn_pct
            sequence_item = self._get_next_sequence_item(is_txn)
            await self.start_item(sequence_item)
            if is_txn:
                num_txn += 1
            await self.finish_item(sequence_item)
        sequence_item = self._get_next_sequence_item(False)
        await self.start_item(sequence_item)
        await self.finish_item(sequence_item)
