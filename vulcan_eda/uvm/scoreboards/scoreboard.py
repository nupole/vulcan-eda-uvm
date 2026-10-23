import pyuvm

class Scoreboard(pyuvm.uvm_scoreboard):
    def build_phase(self):
        self.actual_data_analysis_fifo = pyuvm.uvm_tlm_analysis_fifo('actual_data_analysis_fifo', self)
        self.expected_data_analysis_fifo = pyuvm.uvm_tlm_analysis_fifo('expected_data_analysis_fifo', self)

    async def run_phase(self):
        while True:
            actual_data = await self.actual_data_analysis_fifo.get()
            expected_data = await self.expected_data_analysis_fifo.get()
            if actual_data != expected_data:
                raise AssertionError(f'Actual data ({actual_data}) does not equal expected data ({expected_data})!')

    def check_phase(self):
        if not self.actual_data_analysis_fifo.is_empty():
            raise AssertionError('Actual data analysis fifo is not empty!')
        if not self.expected_data_analysis_fifo.is_empty():
            raise AssertionError('Expected data analysis fifo is not empty!')
