import ast
import pathlib

import vulcan_eda.uvm

PACKAGE_DIR = pathlib.Path(vulcan_eda.uvm.__file__).parent
PROTOCOLS_DIR = PACKAGE_DIR / "protocols"
TESTS_DIR = pathlib.Path(__file__).parents[2]

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

def unsorted_imports(directory):
    for path in sorted(directory.rglob("*.py")):
        tree = ast.parse(path.read_text())
        modules = [node.module if isinstance(node, ast.ImportFrom) else node.names[0].name for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
        for package in ("vulcan_eda", "tests"):
            package_modules = [module for module in modules if module and module.split(".")[0] == package]
            if package_modules != sorted(package_modules):
                yield f"{path.relative_to(directory)} imports {package} modules out of order"

def test_library_imports_are_sorted():
    assert list(unsorted_imports(PACKAGE_DIR)) == []

def test_test_imports_are_sorted():
    assert list(unsorted_imports(TESTS_DIR)) == []

def protocol_imports_from_core():
    for path in sorted(PACKAGE_DIR.rglob("*.py")):
        if PROTOCOLS_DIR in path.parents:
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            modules = [alias.name for alias in node.names] if isinstance(node, ast.Import) else [node.module] if isinstance(node, ast.ImportFrom) else []
            if any(module and module.startswith("vulcan_eda.uvm.protocols") for module in modules):
                yield f"{path.relative_to(PACKAGE_DIR)}:{node.lineno} imports {', '.join(modules)}"

def test_core_does_not_import_protocols():
    assert list(protocol_imports_from_core()) == []
