import pyuvm

from vulcan_eda.uvm.protocols.axi.stream.sequences.axi_stream_beat_sequence import AxiStreamBeatSequence
from vulcan_eda.uvm.sequences.translation_sequence import TranslationSequence

class AxiStreamPacketToBeatSequence(TranslationSequence):
    async def _translate(self, upper_item):
        config = pyuvm.ConfigDB().get(self.sequencer, "", "axi_stream_config")
        axi_stream_beat_sequence = AxiStreamBeatSequence.create("axi_stream_beat_sequence")
        axi_stream_beat_sequence.beats = upper_item.data.to_beats(config.num_bytes)
        await axi_stream_beat_sequence.start(self.sequencer)
