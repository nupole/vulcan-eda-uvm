import cocotb
import pyuvm

from vulcan_eda.uvm.protocols.axi.mm.configs.axi_config import AxiConfig
from vulcan_eda.uvm.protocols.axi.mm.data.axi_address import AxiAddress
from vulcan_eda.uvm.protocols.axi.mm.data.axi_transaction import AxiTransaction
from vulcan_eda.uvm.protocols.axi.mm.data.axi_write_data import AxiWriteData
from vulcan_eda.uvm.sequences.data_sequence import DataSequence
from vulcan_eda.uvm.sequences.translation_sequence import TranslationSequence
from vulcan_eda.uvm.sequences.valid_data_sequence import ValidDataSequence

class AxiTransactionToChannelSequence(TranslationSequence):
    channels = ("aw", "w", "b", "ar", "r")
    uses_responses = True

    async def body(self):
        self._config = pyuvm.ConfigDB().get(self.upper_sequencer, "", "axi_config")
        await self._send(DataSequence, "b", (1,))
        await self._send(DataSequence, "r", (1,))
        await super().body()

    async def _translate(self, upper_item):
        txn = upper_item.data
        if self._config.profile is AxiConfig.Profile.LITE and not (txn.num_beats == 1):
            raise ValueError("AXI4-Lite transactions must be a single beat")
        address = AxiAddress(txn.address, self._config.bytes_per_beat, num_beats=txn.num_beats, id=txn.id, burst=txn.burst)
        if txn.access is AxiTransaction.Access.WRITE:
            strobe = 2 ** self._config.bytes_per_beat - 1
            address_task = cocotb.start_soon(self._send(ValidDataSequence, "aw", (address,)))
            write_data = [AxiWriteData(data, strobe, last=(beat == txn.num_beats - 1)) for beat, data in enumerate(txn.data)]
            await self._send(ValidDataSequence, "w", write_data)
            await address_task
        else:
            await self._send(ValidDataSequence, "ar", (address,))
        return await self.responses.get()

    async def _send(self, sequence_type, channel, data_generator):
        sequence = sequence_type.create(f"{channel}_sequence")
        sequence.data_generator = data_generator
        await sequence.start(self.lower_sequencers[channel])
