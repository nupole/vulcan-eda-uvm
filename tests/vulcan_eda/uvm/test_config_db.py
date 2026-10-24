import ast
import pathlib

import vulcan_eda.uvm

PACKAGE_DIR = pathlib.Path(vulcan_eda.uvm.__file__).parent
BASE_CONFIG = PACKAGE_DIR / "configs" / "base_config.py"

def config_db_calls():
    for path in sorted(PACKAGE_DIR.rglob("*.py")):
        if path == BASE_CONFIG:
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Attribute) and node.attr == "ConfigDB":
                yield f"{path.relative_to(PACKAGE_DIR)}:{node.lineno} uses ConfigDB directly"

def test_library_reaches_config_db_only_through_base_config():
    assert list(config_db_calls()) == []
