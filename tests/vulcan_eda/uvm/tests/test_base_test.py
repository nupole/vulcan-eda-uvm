import logging

import pytest
import pyuvm

from vulcan_eda.uvm.tests import BaseTest

@pytest.fixture
def base_test(monkeypatch, caplog):
    for option in ("max_quit_count", "MAX_QUIT_COUNT", "UVM_MAX_QUIT_COUNT", "UVM_VERBOSITY"):
        monkeypatch.delenv(option, raising=False)
    uvm_logger = logging.getLogger("uvm")
    uvm_logger.addHandler(caplog.handler)
    yield lambda: BaseTest.create("uvm_test_top", None)
    uvm_logger.removeHandler(caplog.handler)
    pyuvm.uvm_report_server.get().shutdown()
    pyuvm.set_sv_uvm_style_reporting_enabled(False)

def report(base_test):
    component = pyuvm.uvm_component("component", base_test)
    component.uvm_report.error("ERROR", "first")
    component.uvm_report.error("ERROR", "second")
    component.uvm_report.info("MEDIUM", "medium", pyuvm.UVM_MEDIUM)
    component.uvm_report.info("HIGH", "high", pyuvm.UVM_HIGH)

def messages(caplog):
    return [record.getMessage() for record in caplog.records if record.name.startswith("uvm.")]

def test_reports_through_the_report_server(base_test):
    report(base_test())
    assert pyuvm.uvm_report_server.get().get_stats().error_count == 2

def test_reports_every_error_and_medium_verbosity_by_default(base_test, caplog):
    report(base_test())
    assert messages(caplog) == ["first", "second", "medium"]

def test_keeps_a_given_quit_count(base_test, caplog, monkeypatch):
    monkeypatch.setenv("UVM_MAX_QUIT_COUNT", "1")
    report(base_test())
    assert "second" not in messages(caplog)

def test_keeps_a_given_verbosity(base_test, caplog, monkeypatch):
    monkeypatch.setenv("UVM_VERBOSITY", "HIGH")
    report(base_test())
    assert "high" in messages(caplog)
