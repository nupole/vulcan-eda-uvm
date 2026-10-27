import collections
import logging

import cocotb
import cocotb.simtime
import cocotb.triggers
import pyuvm
import pyuvm.uvm_reporting.uvm_runtime_options

from vulcan_eda.uvm.configs.tests.verdict_config import VerdictConfig

class BaseTest(pyuvm.uvm_test):
    class _ErrorRecorder(logging.Handler):
        def __init__(self):
            super().__init__(logging.ERROR)
            self.counts = collections.Counter()
            self.first_error = None

        def emit(self, record):
            if not getattr(record, "_uvm_report_record", False):
                return
            source = getattr(record, "uvm_full_name", record.name)
            self.counts[(source, getattr(record, "report_id", ""))] += 1
            if self.first_error is None:
                try:
                    sim_time = f" at {cocotb.simtime.get_sim_time('ns'):.2f}ns"
                except RuntimeError:
                    sim_time = ""
                self.first_error = f"first{sim_time} from {source}: {record.getMessage()}"

    drain_time_ns = 0
    timeout_us = None

    # cocotb holds the regression seed only while test modules are collected, which is when this module is imported
    _REGRESSION_SEED = getattr(cocotb, "RANDOM_SEED", None)
    _QUIT_COUNT_OPTIONS = ("max_quit_count", "MAX_QUIT_COUNT", "UVM_MAX_QUIT_COUNT")
    _VERBOSITY_OPTION = "UVM_VERBOSITY"

    def __init__(self, name, parent=None):
        pyuvm.set_sv_uvm_style_reporting_enabled(True)
        super().__init__(name, parent)
        VerdictConfig(self).set(self, "*")
        self._error_recorder = BaseTest._ErrorRecorder()
        logging.getLogger("uvm").addHandler(self._error_recorder)

    def configure_uvm_reporting(self):
        report_server = super().configure_uvm_reporting()
        if pyuvm.uvm_reporting.uvm_runtime_options.get_runtime_option(self._QUIT_COUNT_OPTIONS) is None:
            report_server.policy.max_quit_count = 0
        if pyuvm.uvm_reporting.uvm_runtime_options.get_runtime_option(self._VERBOSITY_OPTION) is None:
            self.set_report_verbosity(pyuvm.UVM_MEDIUM)
        return report_server

    def end_of_elaboration_phase(self):
        self.uvm_report.info("TOPOLOGY", "\n".join(["topology:", *BaseTest._topology(self, 0)]), pyuvm.UVM_FULL)
        overrides = list(BaseTest._factory_overrides())
        self.uvm_report.info("FACTORY", "\n".join(["factory overrides:", *overrides]) if overrides else "factory overrides: none", pyuvm.UVM_FULL)

    async def run_phase(self):
        self.raise_objection()
        if self.timeout_us is None:
            await self._stimulus_and_drain()
        else:
            try:
                await cocotb.triggers.with_timeout(self._stimulus_and_drain(), self.timeout_us, "us")
            except cocotb.triggers.SimTimeoutError:
                self.uvm_report.error("TIMEOUT", f"stimulus and drain did not finish within {self.timeout_us}us")
        self.drop_objection()

    async def stimulus(self):
        raise NotImplementedError

    async def _stimulus_and_drain(self):
        await self.stimulus()
        if self.drain_time_ns:
            await cocotb.triggers.Timer(self.drain_time_ns, unit="ns")

    def final_phase(self):
        logging.getLogger("uvm").removeHandler(self._error_recorder)
        report_server = pyuvm.uvm_report_server.get()
        report_server.log_summary(self.logger)
        failure = report_server.failure_message()
        if failure is not None:
            failure = self._failure_reason(failure)
            self.uvm_report.error("TEST_FAILED", failure)
        report_server.log_final_status(self.logger, prior_failure_msg=failure)
        if failure is not None:
            raise AssertionError(failure)

    @staticmethod
    def _topology(component, depth):
        yield f"{'  ' * depth}{component.get_name()} ({type(component).__name__})"
        for child in component.get_children():
            if not isinstance(child, pyuvm.uvm_export_base):
                yield from BaseTest._topology(child, depth + 1)

    @staticmethod
    def _factory_overrides():
        for original, override in pyuvm.uvm_factory().fd.overrides.items():
            original_name = getattr(original, "__name__", original)
            if override.type_override is not None:
                yield f"{original_name} => {override.type_override.__name__}"
            for path, inst_override in override.inst_overrides.items():
                yield f"{original_name} at {path} => {inst_override.__name__}"

    def _failure_reason(self, failure):
        lines = [failure]
        lines += [f"{count} {report_id} from {source}" for (source, report_id), count in self._error_recorder.counts.most_common()]
        if self._error_recorder.first_error is not None:
            lines.append(self._error_recorder.first_error)
        if BaseTest._REGRESSION_SEED is not None:
            lines.append(f"rerun with COCOTB_RANDOM_SEED={BaseTest._REGRESSION_SEED}")
        return "\n".join(lines)
