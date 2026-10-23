import pyuvm

class TranslationLayer(pyuvm.uvm_component):
    def build_phase(self):
        self.lower_sequencer = None
        self._config = pyuvm.ConfigDB().get(self, "", "config")
        if self._config.translation_sequence_type is not None:
            self.sequencer = pyuvm.uvm_sequencer.create("sequencer", self)
            self._forward_configs(self.sequencer)
        if self._config.translation_subscriber_type is not None:
            self.subscriber = self._config.translation_subscriber_type.create("subscriber", self)
            self._forward_configs(self.subscriber)
            self.analysis_export = self.subscriber.analysis_export
            self.analysis_port = pyuvm.uvm_analysis_port("analysis_port", self)

    def connect_phase(self):
        if self._config.translation_subscriber_type is not None:
            self.subscriber.analysis_port.connect(self.analysis_port)

    def end_of_elaboration_phase(self):
        if self._config.translation_sequence_type is None:
            return
        if self.lower_sequencer is None:
            raise pyuvm.UVMError(f"{self.get_full_name()} has no lower_sequencer; set it in the env's connect_phase")
        self._forward_configs(self.lower_sequencer)

    async def run_phase(self):
        if self._config.translation_sequence_type is None:
            return
        translation_sequence = self._config.translation_sequence_type.create("translation_sequence")
        translation_sequence.upper_sequencer = self.sequencer
        await translation_sequence.start(self.lower_sequencer)

    def _forward_configs(self, component):
        for key, config in self._config.forwarded_configs.items():
            pyuvm.ConfigDB().set(component, "", key, config)
