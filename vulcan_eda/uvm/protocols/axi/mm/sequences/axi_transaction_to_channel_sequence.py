import cocotb

from vulcan_eda.uvm.protocols.axi.mm.configs.axi_config import AxiConfig
from vulcan_eda.uvm.protocols.axi.mm.configs.sequences.axi_transaction_to_channel_sequence_config import AxiTransactionToChannelSequenceConfig
from vulcan_eda.uvm.protocols.axi.mm.data.axi_address import AxiAddress
from vulcan_eda.uvm.protocols.axi.mm.data.axi_transaction import AxiTransaction
from vulcan_eda.uvm.protocols.axi.mm.data.axi_write_data import AxiWriteData
from vulcan_eda.uvm.sequences.translation_sequence import TranslationSequence
from vulcan_eda.uvm.sequences.valid_data_sequence import ValidDataSequence

class AxiTransactionToChannelSequence(TranslationSequence):
    channels = ("aw", "w", "ar")
    uses_responses = True

    async def translate(self, upper_item):
        self._config = AxiConfig.get(self.upper_sequencer)
        txn = upper_item.data
        if self._config.profile is AxiConfig.Profile.LITE and not (txn.num_beats == 1):
            raise ValueError("AXI4-Lite transactions must be a single beat")
        self._sequence_config = AxiTransactionToChannelSequenceConfig.get(self.upper_sequencer)
        address = AxiAddress(address=txn.address, bytes_per_beat=self._config.bytes_per_beat, num_beats=txn.num_beats, id=txn.id, burst=txn.burst)
        if txn.access is AxiTransaction.Access.WRITE:
            strobe = 2 ** self._config.bytes_per_beat - 1
            address_task = cocotb.start_soon(self._send("aw", (address,), self._sequence_config.awvalid_generator))
            write_data = [AxiWriteData(data=data, strobe=strobe, last=(beat == txn.num_beats - 1)) for beat, data in enumerate(txn.data)]
            await self._send("w", write_data, self._sequence_config.wvalid_generator)
            await address_task
        else:
            await self._send("ar", (address,), self._sequence_config.arvalid_generator)
        return await self.responses.get()

    async def _send(self, channel, data_generator, valid_generator):
        valid_data_sequence = ValidDataSequence.create(f"{channel}_sequence")
        valid_data_sequence.valid_generator = valid_generator
        valid_data_sequence.data_generator = data_generator
        await valid_data_sequence.start(self.lower_sequencers[channel])
