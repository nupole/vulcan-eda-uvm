import pathlib

import pytest

ROOT_DIR = pathlib.Path(__file__).parent

@pytest.fixture
def build_dir(request):
    return ROOT_DIR / "build" / request.path.with_suffix("").relative_to(ROOT_DIR / "tests")
