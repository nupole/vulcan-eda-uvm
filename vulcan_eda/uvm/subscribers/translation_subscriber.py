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
        self._translated_count = 0

    def write(self, channel, lower_item):
        for upper_item in self.translate(channel, lower_item):
            self._translated_count += 1
            self.uvm_report.info("TRANSLATED", f"translated {upper_item}", pyuvm.UVM_HIGH)
            self.analysis_port.write(upper_item)

    def report_phase(self):
        self.uvm_report.info("SUMMARY", f"translated {self._translated_count} item(s)", pyuvm.UVM_LOW)

    def translate(self, channel, lower_item):
        raise NotImplementedError
