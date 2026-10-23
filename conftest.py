import collections
import pathlib

import pytest
import pyuvm

ROOT_DIR = pathlib.Path(__file__).parent

class RecordingSequencer(pyuvm.uvm_sequencer):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.items = []

    async def start_item(self, item):
        pass

    async def finish_item(self, item):
        self.items.append(item)

class UpperSequencer:
    class Drained(Exception):
        pass

    def __init__(self):
        self.items = collections.deque()
        self.done_items = []
        self.seq_item_export = self

    async def get_next_item(self):
        if not self.items:
            raise UpperSequencer.Drained()
        self._current_item = self.items.popleft()
        return self._current_item

    def item_done(self):
        self.done_items.append(self._current_item)

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
    return UpperSequencer()
