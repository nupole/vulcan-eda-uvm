from vulcan_eda.uvm.protocols.axi.stream.configs.axi_stream_config import AxiStreamConfig
from vulcan_eda.uvm.protocols.axi.stream.configs.sequences.axi_stream_packet_to_beat_sequence_config import AxiStreamPacketToBeatSequenceConfig
from vulcan_eda.uvm.sequences.translation_sequence import TranslationSequence
from vulcan_eda.uvm.sequences.valid_data_sequence import ValidDataSequence

class AxiStreamPacketToBeatSequence(TranslationSequence):
    channels = ("stream",)

    async def translate(self, upper_item):
        config = AxiStreamConfig.get(self.upper_sequencer)
        sequence_config = AxiStreamPacketToBeatSequenceConfig.get(self.upper_sequencer)
        valid_data_sequence = ValidDataSequence.create("valid_data_sequence")
        valid_data_sequence.valid_generator = sequence_config.valid_generator
        valid_data_sequence.data_generator = upper_item.data.to_beats(config.num_bytes)
        await valid_data_sequence.start(self.lower_sequencers["stream"])
