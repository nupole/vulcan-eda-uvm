import pyuvm

class Monitor(pyuvm.uvm_monitor):
    def build_phase(self):
        self._interface = pyuvm.ConfigDB().get(self, "", "interface")
        self.analysis_port = pyuvm.uvm_analysis_port('analysis_port', self)

    async def run_phase(self):
        while True:
            data = await self._interface.get()
            self.analysis_port.write(data)
