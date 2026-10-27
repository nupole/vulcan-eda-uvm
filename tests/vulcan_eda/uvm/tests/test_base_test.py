import pytest
import pyuvm

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

def test_passes_without_errors(base_test, caplog):
    base_test().final_phase()
    assert "TEST_STATUS: PASSED" in messages(caplog)

def test_fails_once_at_the_end_on_reported_errors(base_test, caplog):
    test = base_test()
    report(test)
    with pytest.raises(AssertionError, match="2 error"):
        test.final_phase()
    assert "TEST_STATUS: FAILED" in messages(caplog)
