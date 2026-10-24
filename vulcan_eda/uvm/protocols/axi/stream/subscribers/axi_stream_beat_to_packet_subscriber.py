from vulcan_eda.uvm.protocols.axi.stream.configs.axi_stream_config import AxiStreamConfig
from vulcan_eda.uvm.protocols.axi.stream.data.axi_stream_packet import AxiStreamPacket
from vulcan_eda.uvm.subscribers.translation_subscriber import TranslationSubscriber

class AxiStreamBeatToPacketSubscriber(TranslationSubscriber):
    channels = ("stream",)

    def build_phase(self):
        super().build_phase()
        config = AxiStreamConfig.get(self)
        self._num_bytes = config.num_bytes
        self._beats = []

    def translate(self, channel, beat):
        self._beats.append(beat)
        if beat.last:
            yield AxiStreamPacket.from_beats(self._beats, self._num_bytes)
            self._beats = []
