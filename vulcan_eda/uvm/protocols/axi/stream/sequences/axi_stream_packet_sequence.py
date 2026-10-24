import random

import pyuvm

from vulcan_eda.uvm.protocols.axi.stream.configs.axi_stream_config import AxiStreamConfig
from vulcan_eda.uvm.protocols.axi.stream.configs.sequences.axi_stream_packet_sequence_config import AxiStreamPacketSequenceConfig
from vulcan_eda.uvm.protocols.axi.stream.data.axi_stream_packet import AxiStreamPacket
from vulcan_eda.uvm.sequences.data_sequence import DataSequenceItem

class AxiStreamPacketSequence(pyuvm.uvm_sequence):
    def _configure(self):
        config = AxiStreamPacketSequenceConfig.get(self.sequencer)
        self.num_packets = config.num_packets
        self.min_num_beats = config.min_num_beats
        self.max_num_beats = config.max_num_beats
        axi_stream_config = AxiStreamConfig.get(self.sequencer)
        self._num_bytes = axi_stream_config.num_bytes

    async def body(self):
        self._configure()
        for _ in range(self.num_packets):
            sequence_item = DataSequenceItem('axi_stream_packet_sequence_item', self._get_next_packet())
            await self.start_item(sequence_item)
            await self.finish_item(sequence_item)

    def _get_next_packet(self):
        raise NotImplementedError

class RandomAxiStreamPacketSequence(AxiStreamPacketSequence):
    def _get_next_packet(self):
        num_beats = random.randint(self.min_num_beats, self.max_num_beats)
        return AxiStreamPacket(random.randbytes(num_beats * self._num_bytes))
