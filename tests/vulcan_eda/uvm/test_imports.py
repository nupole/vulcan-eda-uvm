import ast
import pathlib

import vulcan_eda.uvm

PACKAGE_DIR = pathlib.Path(vulcan_eda.uvm.__file__).parent

def package_imports():
    for path in sorted(PACKAGE_DIR.rglob("*.py")):
        if path.name == "__init__.py":
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("vulcan_eda.uvm"):
                module_path = PACKAGE_DIR.joinpath(*node.module.split(".")[2:])
                if (module_path / "__init__.py").exists():
                    yield f"{path.relative_to(PACKAGE_DIR)}:{node.lineno} imports from package {node.module}"

def test_library_modules_import_from_full_module_paths():
    assert list(package_imports()) == []
