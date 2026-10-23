import pyuvm

class TranslationLayer(pyuvm.uvm_component):
    def build_phase(self):
        self.lower_sequencer = None
        self._config = pyuvm.ConfigDB().get(self, "", "config")
        self.sequencer = pyuvm.uvm_sequencer.create("sequencer", self)
        for key, config in self._config.forwarded_configs.items():
            pyuvm.ConfigDB().set(self, "sequencer", key, config)

    def end_of_elaboration_phase(self):
        if self.lower_sequencer is None:
            raise pyuvm.UVMError(f"{self.get_full_name()} has no lower_sequencer; set it in the env's connect_phase")
        for key, config in self._config.forwarded_configs.items():
            pyuvm.ConfigDB().set(self.lower_sequencer, "", key, config)

    async def run_phase(self):
        translation_sequence = self._config.translation_sequence_type.create("translation_sequence")
        translation_sequence.upper_sequencer = self.sequencer
        await translation_sequence.start(self.lower_sequencer)
