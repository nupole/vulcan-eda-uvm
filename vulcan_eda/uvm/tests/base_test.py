import pyuvm
import pyuvm.uvm_reporting.uvm_runtime_options

class BaseTest(pyuvm.uvm_test):
    _QUIT_COUNT_OPTIONS = ("max_quit_count", "MAX_QUIT_COUNT", "UVM_MAX_QUIT_COUNT")
    _VERBOSITY_OPTION = "UVM_VERBOSITY"

    def __init__(self, name, parent=None):
        pyuvm.set_sv_uvm_style_reporting_enabled(True)
        super().__init__(name, parent)

    def configure_uvm_reporting(self):
        report_server = super().configure_uvm_reporting()
        if pyuvm.uvm_reporting.uvm_runtime_options.get_runtime_option(self._QUIT_COUNT_OPTIONS) is None:
            report_server.policy.max_quit_count = 0
        if pyuvm.uvm_reporting.uvm_runtime_options.get_runtime_option(self._VERBOSITY_OPTION) is None:
            self.set_report_verbosity(pyuvm.UVM_MEDIUM)
        return report_server

    def final_phase(self):
        report_server = pyuvm.uvm_report_server.get()
        report_server.log_summary(self.logger)
        failure = report_server.log_final_status(self.logger)
        if failure is not None:
            raise AssertionError(failure)
