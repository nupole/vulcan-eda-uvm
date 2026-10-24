import pyuvm

from vulcan_eda.uvm.generators.constant_generator import ConstantGenerator
from vulcan_eda.uvm.sequences.data_sequence_item import DataSequenceItem
from vulcan_eda.uvm.sequences.idle_sequence_item import IdleSequenceItem

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
                await self._send(IdleSequenceItem('idle_sequence_item'))
            await self._send(DataSequenceItem('data_sequence_item', data))

    def _next_valid(self, valids):
        valid = next(valids, None)
        if valid is None:
            raise ValueError("valid_generator ran out before data_generator")
        return valid

    async def _send(self, sequence_item):
        await self.start_item(sequence_item)
        await self.finish_item(sequence_item)
