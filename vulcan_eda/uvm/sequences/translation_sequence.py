import pyuvm

class TranslationSequence(pyuvm.uvm_sequence):
    channels = ()

    def __init__(self, name):
        super().__init__(name)
        self.upper_sequencer = None
        self.lower_sequencers = {}

    async def body(self):
        while True:
            upper_item = await self.upper_sequencer.get_next_item()
            await self._translate(upper_item)
            self.upper_sequencer.seq_item_export.item_done()

    async def _translate(self, upper_item):
        raise NotImplementedError
