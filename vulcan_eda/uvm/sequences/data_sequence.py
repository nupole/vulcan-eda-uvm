import pyuvm

from vulcan_eda.uvm.sequences.data_sequence_item import DataSequenceItem

class DataSequence(pyuvm.uvm_sequence):
    _data_generator = None

    @property
    def data_generator(self):
        return self._data_generator

    @data_generator.setter
    def data_generator(self, data_generator):
        iter(data_generator)
        self._data_generator = data_generator

    async def body(self):
        if self._data_generator is None:
            raise ValueError("data_generator must be set before starting a DataSequence")
        for data in self._data_generator:
            sequence_item = DataSequenceItem('data_sequence_item', data)
            await self.start_item(sequence_item)
            await self.finish_item(sequence_item)
