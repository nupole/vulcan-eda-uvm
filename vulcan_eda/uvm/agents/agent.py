import pyuvm

from vulcan_eda.uvm.drivers.driver import Driver
from vulcan_eda.uvm.monitors.monitor import Monitor

class Agent(pyuvm.uvm_agent):
    def build_phase(self):
        super().build_phase()

        interface = pyuvm.ConfigDB().get(self, "", "interface")

        if self.active():
            self.sequencer = pyuvm.uvm_sequencer.create("sequencer", self)

            pyuvm.ConfigDB().set(self, "driver", "interface", interface)
            self._driver = Driver.create("driver", self)

        pyuvm.ConfigDB().set(self, "monitor", "interface", interface)
        self._monitor = Monitor.create("monitor", self)

        self.analysis_port = pyuvm.uvm_analysis_port("analysis_port", self)

    def connect_phase(self):
        if self.active():
            self._driver.seq_item_port.connect(self.sequencer.seq_item_export)
        self._monitor.analysis_port.connect(self.analysis_port)
