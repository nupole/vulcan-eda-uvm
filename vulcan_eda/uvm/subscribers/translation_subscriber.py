import functools

import pyuvm

class TranslationSubscriber(pyuvm.uvm_component):
    channels = ()

    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.analysis_exports = {
            channel: pyuvm.uvm_subscriber.uvm_AnalysisImp(f"{channel}_analysis_export", self, functools.partial(self.write, channel))
            for channel in self.channels
        }

    def build_phase(self):
        self.analysis_port = pyuvm.uvm_analysis_port("analysis_port", self)

    def write(self, channel, lower_item):
        for upper_item in self.translate(channel, lower_item):
            self.analysis_port.write(upper_item)

    def translate(self, channel, lower_item):
        raise NotImplementedError
