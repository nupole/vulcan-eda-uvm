import pytest
import pyuvm

from vulcan_eda.uvm.tests import BaseTest

FAILURE_REASON = "\n".join([
    "Detected report failures at termination (1 info(s), 0 warning(s), 2 error(s), 0 fatal(s))",
    "2 ERROR from uvm_test_top.component",
    "first from uvm_test_top.component: first",
])

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
    assert messages(caplog)[-2:] == [FAILURE_REASON, "TEST_STATUS: FAILED"]

def test_names_the_seed_to_rerun_a_failure(base_test, monkeypatch):
    monkeypatch.setattr(BaseTest, "_REGRESSION_SEED", 1234)
    test = base_test()
    report(test)
    with pytest.raises(AssertionError) as failure:
        test.final_phase()
    assert str(failure.value) == f"{FAILURE_REASON}\nrerun with COCOTB_RANDOM_SEED=1234"

def test_counts_errors_per_component_and_report_id(base_test):
    test = base_test()
    report(test)
    pyuvm.uvm_component("other", test).uvm_report.error("OTHER", "third")
    with pytest.raises(AssertionError) as failure:
        test.final_phase()
    assert str(failure.value).splitlines()[1:3] == ["2 ERROR from uvm_test_top.component", "1 OTHER from uvm_test_top.other"]
