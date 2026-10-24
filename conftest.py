import pathlib

import pytest
import pyuvm

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
