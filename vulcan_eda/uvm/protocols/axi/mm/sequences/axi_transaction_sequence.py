import random

import pyuvm

from vulcan_eda.uvm.protocols.axi.mm.configs.axi_config import AxiConfig
from vulcan_eda.uvm.protocols.axi.mm.configs.sequences.axi_transaction_sequence_config import AxiTransactionSequenceConfig
from vulcan_eda.uvm.protocols.axi.mm.data.axi_transaction import AxiTransaction
from vulcan_eda.uvm.sequences.data_sequence import DataSequenceItem

class AxiTransactionSequence(pyuvm.uvm_sequence):
    def configure(self):
        config = AxiTransactionSequenceConfig.get(self.sequencer)
        self.num_txn = config.num_txn
        self.write_pct = config.write_pct
        axi_config = AxiConfig.get(self.sequencer)
        self._bytes_per_beat = axi_config.bytes_per_beat
        self.min_address = config.min_address
        if config.max_address is None:
            self.max_address = 2 ** axi_config.address_width - 1
        else:
            self.max_address = config.max_address

    async def body(self):
        self.configure()
        for _ in range(self.num_txn):
            sequence_item = DataSequenceItem('axi_transaction_sequence_item', self.get_next_txn())
            await self.start_item(sequence_item)
            await self.finish_item(sequence_item)
            await self.get_response()

    def get_next_txn(self):
        raise NotImplementedError

class RandomAxiTransactionSequence(AxiTransactionSequence):
    def configure(self):
        super().configure()
        self._min_beat_address = -(-self.min_address // self._bytes_per_beat)
        self._max_beat_address = self.max_address // self._bytes_per_beat
        if not (self._min_beat_address <= self._max_beat_address):
            raise ValueError(f"no {self._bytes_per_beat}-byte aligned address between min_address and max_address")

    def get_next_txn(self):
        address = random.randint(self._min_beat_address, self._max_beat_address) * self._bytes_per_beat
        if random.randint(1, 100) <= self.write_pct:
            data = random.getrandbits(8 * self._bytes_per_beat)
            return AxiTransaction(access=AxiTransaction.Access.WRITE, address=address, data=(data,))
        return AxiTransaction(access=AxiTransaction.Access.READ, address=address)
