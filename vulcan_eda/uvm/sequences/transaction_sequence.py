import random

import pyuvm

class TransactionSequence(pyuvm.uvm_sequence):
    def __init__(self, name):
        super().__init__(name)

    @property
    def txn_pct(self):
        return self._txn_pct

    @txn_pct.setter
    def txn_pct(self, value):
        if not (0 <= value <= 100):
            raise ValueError("txn_pct must be between 0 and 100")
        self._txn_pct = value

    @property
    def max_num_txn(self):
        return self._max_num_txn

    @max_num_txn.setter
    def max_num_txn(self, value):
        if value < 0:
            raise ValueError("max_num_txn must be positive")
        self._max_num_txn = value

    async def body(self):
        self.txn_pct = pyuvm.ConfigDB().get(self.sequencer, "", "txn_pct", 100)
        self.max_num_txn = pyuvm.ConfigDB().get(self.sequencer, "", "max_num_txn", 10)
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
