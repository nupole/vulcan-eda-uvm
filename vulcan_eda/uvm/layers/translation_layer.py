import pyuvm

from vulcan_eda.uvm.configs.layers.translation_layer_config import TranslationLayerConfig

class TranslationLayer(pyuvm.uvm_component):
    def build_phase(self):
        self.lower_sequencers = {}
        self.responses = None
        self._config = TranslationLayerConfig.get(self)
        if self._config.translation_sequence_type is not None:
            self.sequencer = pyuvm.uvm_sequencer.create("sequencer", self)
            self._forward_configs(self.sequencer)
        if self._config.translation_subscriber_type is not None:
            self.subscriber = self._config.translation_subscriber_type.create("subscriber", self)
            self._forward_configs(self.subscriber)
            self.analysis_exports = self.subscriber.analysis_exports
            self.analysis_port = pyuvm.uvm_analysis_port("analysis_port", self)
        if self._config.translation_sequence_type is not None and self._config.translation_sequence_type.uses_responses:
            self.responses = pyuvm.uvm_tlm_analysis_fifo("responses", self)

    def connect_phase(self):
        if self._config.translation_subscriber_type is not None:
            self.subscriber.analysis_port.connect(self.analysis_port)
        if self.responses is not None:
            self.subscriber.analysis_port.connect(self.responses.analysis_export)

    def end_of_elaboration_phase(self):
        if self._config.translation_sequence_type is None:
            return
        channels = self._config.translation_sequence_type.channels
        missing = [channel for channel in channels if channel not in self.lower_sequencers]
        if missing:
            raise pyuvm.UVMError(f"{self.get_full_name()} has no lower_sequencers for {', '.join(missing)}; set them in the env's connect_phase")
        unknown = [channel for channel in self.lower_sequencers if channel not in channels]
        if unknown:
            raise pyuvm.UVMError(f"{self.get_full_name()} has lower_sequencers for unknown channels {', '.join(unknown)}; expected {', '.join(channels)}")
        for lower_sequencer in self.lower_sequencers.values():
            self._forward_configs(lower_sequencer)

    async def run_phase(self):
        if self._config.translation_sequence_type is None:
            return
        translation_sequence = self._config.translation_sequence_type.create("translation_sequence")
        translation_sequence.upper_sequencer = self.sequencer
        translation_sequence.lower_sequencers = self.lower_sequencers
        translation_sequence.responses = self.responses
        await translation_sequence.start()

    def _forward_configs(self, component):
        for forwarded_config in self._config.forwarded_configs:
            forwarded_config.set(component)
