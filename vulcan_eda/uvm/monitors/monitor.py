import pyuvm

from vulcan_eda.uvm.configs.agents.agent_config import AgentConfig

class Monitor(pyuvm.uvm_monitor):
    def build_phase(self):
        self._interface = AgentConfig.get(self).interface
        self._monitored_count = 0
        self.analysis_port = pyuvm.uvm_analysis_port('analysis_port', self)

    async def run_phase(self):
        while True:
            data = await self._interface.get_data()
            self._monitored_count += 1
            if pyuvm.UVM_HIGH <= self.get_report_verbosity():
                self.uvm_report.info("MONITORED", f"monitored {data}", pyuvm.UVM_HIGH)
            self.analysis_port.write(data)

    def report_phase(self):
        self.uvm_report.info("SUMMARY", f"monitored {self._monitored_count} item(s)", pyuvm.UVM_LOW)
