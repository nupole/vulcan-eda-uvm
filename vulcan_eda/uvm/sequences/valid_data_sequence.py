import random

import pyuvm

from vulcan_eda.uvm.configs.sequences.random_data_sequence_config import RandomDataSequenceConfig
from vulcan_eda.uvm.generators.constant_generator import ConstantGenerator
from vulcan_eda.uvm.sequences.transaction_sequence import TransactionSequence

class ValidDataSequenceItem(pyuvm.uvm_sequence_item):
    def __init__(self, name, valid, data):
        super().__init__(name)
        self.valid = valid
        self.data = data

class ValidDataSequence(pyuvm.uvm_sequence):
    _valid_generator = ConstantGenerator(True)
    _data_generator = None

    @property
    def valid_generator(self):
        return self._valid_generator

    @valid_generator.setter
    def valid_generator(self, valid_generator):
        iter(valid_generator)
        self._valid_generator = valid_generator

    @property
    def data_generator(self):
        return self._data_generator

    @data_generator.setter
    def data_generator(self, data_generator):
        iter(data_generator)
        self._data_generator = data_generator

    async def body(self):
        if self._data_generator is None:
            raise ValueError("data_generator must be set before starting a ValidDataSequence")
        valids = iter(self._valid_generator)
        for data in self._data_generator:
            while not self._next_valid(valids):
                await self._send(False, None)
            await self._send(True, data)
        await self._send(False, None)

    def _next_valid(self, valids):
        valid = next(valids, None)
        if valid is None:
            raise ValueError("valid_generator ran out before data_generator")
        return valid

    async def _send(self, valid, data):
        sequence_item = ValidDataSequenceItem('valid_data_sequence_item', valid, data)
        await self.start_item(sequence_item)
        await self.finish_item(sequence_item)

class RandomValidDataSequence(TransactionSequence):
    def _configure(self):
        super()._configure()
        config = pyuvm.ConfigDB().get(self.sequencer, "", "random_data_sequence_config", RandomDataSequenceConfig())
        self.min_data = config.min_data
        self.max_data = config.max_data

    def _get_next_sequence_item(self, is_txn):
        data = random.randint(self.min_data, self.max_data)
        return ValidDataSequenceItem('random_valid_data_sequence_item', is_txn, data)

class IterableValidDataSequence(TransactionSequence):
    iterable = ()

    def _configure(self):
        super()._configure()
        data = list(self.iterable)
        if not data:
            raise ValueError("iterable must not be empty")
        self.max_num_txn = len(data)
        self._iterator = iter(data)

    def _get_next_sequence_item(self, is_txn):
        data = next(self._iterator) if is_txn else None
        return ValidDataSequenceItem('iterable_valid_data_sequence_item', is_txn, data)
