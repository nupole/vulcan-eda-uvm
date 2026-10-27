import dataclasses

import cocotb.types
import pyuvm

from vulcan_eda.uvm.configs.tests.verdict_config import VerdictConfig

class Scoreboard(pyuvm.uvm_scoreboard):
    def build_phase(self):
        self.actual_data_analysis_fifo = pyuvm.uvm_tlm_analysis_fifo('actual_data_analysis_fifo', self)
        self.expected_data_analysis_fifo = pyuvm.uvm_tlm_analysis_fifo('expected_data_analysis_fifo', self)
        self._matched_count = 0
        self._mismatched_count = 0

    def end_of_elaboration_phase(self):
        try:
            VerdictConfig.get(self)
        except pyuvm.UVMConfigItemNotFound as error:
            raise pyuvm.UVMError(f"{self.get_full_name()} only reports errors, so something above it must fail the test on them: derive the test from vulcan_eda.uvm.tests.BaseTest or set a vulcan_eda.uvm.configs.tests.VerdictConfig") from error

    async def run_phase(self):
        while True:
            actual_data = await self.actual_data_analysis_fifo.peek()
            expected_data = await self.expected_data_analysis_fifo.get()
            self.actual_data_analysis_fifo.try_get()
            if actual_data == expected_data:
                self._matched_count += 1
                if pyuvm.UVM_HIGH <= self.get_report_verbosity():
                    actual_text, _ = Scoreboard._format_pair(actual_data, expected_data)
                    self.uvm_report.info("MATCHED", f"matched {actual_text}", pyuvm.UVM_HIGH)
            else:
                self._mismatched_count += 1
                actual_text, expected_text = Scoreboard._format_pair(actual_data, expected_data)
                self.uvm_report.error("MISMATCHED", Scoreboard._mismatch_message(actual_data, expected_data, actual_text, expected_text))

    def check_phase(self):
        for kind, analysis_fifo in (("actual", self.actual_data_analysis_fifo), ("expected", self.expected_data_analysis_fifo)):
            if not analysis_fifo.is_empty():
                self.uvm_report.error("UNCOMPARED", f"{analysis_fifo.used()} {kind} data never compared")
        compared_count = self._matched_count + self._mismatched_count
        self.uvm_report.info("SUMMARY", f"compared {compared_count}: {self._matched_count} matched, {self._mismatched_count} mismatched", pyuvm.UVM_LOW)
        if not compared_count:
            self.uvm_report.warning("NOTHING_COMPARED", "compared nothing")

    @staticmethod
    def _mismatch_message(actual_data, expected_data, actual_text, expected_text):
        lines = ["actual data does not equal expected data", f"actual:   {actual_text}", f"expected: {expected_text}"]
        if dataclasses.is_dataclass(actual_data) and type(actual_data) is type(expected_data):
            differing_fields = [field.name for field in dataclasses.fields(actual_data) if getattr(actual_data, field.name) != getattr(expected_data, field.name)]
            lines.append(f"differs in: {', '.join(differing_fields)}")
        return "\n".join(lines)

    @staticmethod
    def _format_pair(actual_data, expected_data):
        pair = (actual_data, expected_data)
        if all(isinstance(data, tuple) for data in pair) and len(actual_data) == len(expected_data):
            formatted_pairs = [Scoreboard._format_pair(*elements) for elements in zip(actual_data, expected_data)]
            return tuple(Scoreboard._format_tuple([formatted_pair[side] for formatted_pair in formatted_pairs]) for side in (0, 1))
        width = max(Scoreboard._width(data) for data in pair)
        if not width or not all(Scoreboard._is_bits(data) for data in pair):
            return str(actual_data), str(expected_data)
        if all(isinstance(data, int) or data.is_resolvable for data in pair):
            return tuple(f"0x{Scoreboard._unsigned(data):0{(width + 3) // 4}x}" for data in pair)
        return tuple(f"0b{Scoreboard._bits(data, width)}" for data in pair)

    @staticmethod
    def _format_tuple(texts):
        return f"({texts[0]},)" if len(texts) == 1 else f"({', '.join(texts)})"

    @staticmethod
    def _width(data):
        if isinstance(data, cocotb.types.LogicArray):
            return len(data)
        return 1 if isinstance(data, cocotb.types.Logic) else 0

    @staticmethod
    def _is_bits(data):
        return isinstance(data, (cocotb.types.Logic, cocotb.types.LogicArray)) or (isinstance(data, int) and data >= 0)

    @staticmethod
    def _unsigned(data):
        return data.to_unsigned() if isinstance(data, cocotb.types.LogicArray) else int(data)

    @staticmethod
    def _bits(data, width):
        return format(data, f"0{width}b") if isinstance(data, int) else str(data).rjust(width, "0")
