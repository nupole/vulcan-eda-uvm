import pyuvm

class Scoreboard(pyuvm.uvm_scoreboard):
    def build_phase(self):
        self.actual_data_analysis_fifo = pyuvm.uvm_tlm_analysis_fifo('actual_data_analysis_fifo', self)
        self.expected_data_analysis_fifo = pyuvm.uvm_tlm_analysis_fifo('expected_data_analysis_fifo', self)
        self._matched_count = 0
        self._mismatched_count = 0

    async def run_phase(self):
        while True:
            actual_data = await self.actual_data_analysis_fifo.peek()
            expected_data = await self.expected_data_analysis_fifo.get()
            self.actual_data_analysis_fifo.try_get()
            if actual_data == expected_data:
                self._matched_count += 1
                self.uvm_report.info("MATCHED", f"matched {actual_data}", pyuvm.UVM_HIGH)
            else:
                self._mismatched_count += 1
                self.uvm_report.error("MISMATCHED", f"actual data {actual_data} does not equal expected data {expected_data}")

    def check_phase(self):
        failures = []
        if self._mismatched_count:
            failures.append(f"{self._mismatched_count} mismatched")
        for kind, analysis_fifo in (("actual", self.actual_data_analysis_fifo), ("expected", self.expected_data_analysis_fifo)):
            if not analysis_fifo.is_empty():
                self.uvm_report.error("UNCOMPARED", f"{analysis_fifo.used()} {kind} data never compared")
                failures.append(f"{analysis_fifo.used()} {kind} never compared")
        compared_count = self._matched_count + self._mismatched_count
        self.uvm_report.info("SUMMARY", f"compared {compared_count}: {self._matched_count} matched, {self._mismatched_count} mismatched", pyuvm.UVM_LOW)
        if not compared_count:
            self.uvm_report.warning("NOTHING_COMPARED", "compared nothing")
        if failures:
            raise AssertionError(f"{self.get_full_name()} failed: {', '.join(failures)}")
