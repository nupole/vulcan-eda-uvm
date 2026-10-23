import pyuvm

from vulcan_eda.uvm.sequences.data_sequence import DataSequenceItem

class TranslationSequence(pyuvm.uvm_sequence):
    channels = ()
    uses_responses = False

    def __init__(self, name):
        super().__init__(name)
        self.upper_sequencer = None
        self.lower_sequencers = {}
        self.responses = None

    async def body(self):
        while True:
            upper_item = await self.upper_sequencer.get_next_item()
            response = await self._translate(upper_item)
            if response is None:
                self.upper_sequencer.seq_item_export.item_done()
            else:
                response_item = DataSequenceItem('translation_response_item', response)
                response_item.set_id_info(upper_item)
                self.upper_sequencer.seq_item_export.item_done(response_item)

    async def _translate(self, upper_item):
        raise NotImplementedError
