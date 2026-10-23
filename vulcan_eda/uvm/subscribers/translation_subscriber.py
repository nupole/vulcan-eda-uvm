import pyuvm

class TranslationSubscriber(pyuvm.uvm_subscriber):
    def build_phase(self):
        self.analysis_port = pyuvm.uvm_analysis_port("analysis_port", self)

    def write(self, lower_item):
        for upper_item in self._translate(lower_item):
            self.analysis_port.write(upper_item)

    def _translate(self, lower_item):
        raise NotImplementedError
