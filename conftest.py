import pathlib

import pytest
import pyuvm

ROOT_DIR = pathlib.Path(__file__).parent

@pytest.fixture(autouse=True)
def reset_pyuvm():
    yield
    pyuvm.uvm_root.clear_singletons()
    pyuvm.uvm_factory().clear_overrides()

@pytest.fixture
def build_dir(request):
    return ROOT_DIR / "build" / request.path.with_suffix("").relative_to(ROOT_DIR / "tests")
