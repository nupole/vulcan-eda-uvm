import logging
import pathlib

import pytest
import pyuvm

from vulcan_eda.uvm.tests import BaseTest

from tests.support.components import RecordingSequencer, RecordingSubscriber, UpperSequencer

ROOT_DIR = pathlib.Path(__file__).parent

@pytest.fixture(autouse=True)
def reset_pyuvm():
    yield
    pyuvm.uvm_root.clear_singletons()
    pyuvm.uvm_factory().clear_overrides()

@pytest.fixture
def build_dir(request):
    return ROOT_DIR / "build" / request.path.with_suffix("").relative_to(ROOT_DIR / "tests")

@pytest.fixture
def recording_sequencer():
    return RecordingSequencer("sequencer", None)

@pytest.fixture
def upper_sequencer():
    return UpperSequencer("upper_sequencer", None)

@pytest.fixture
def recording_subscriber():
    return RecordingSubscriber("recording_subscriber", None)

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
