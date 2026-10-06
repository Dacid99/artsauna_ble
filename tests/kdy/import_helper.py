"""Load kdy_ble modules without importing the HA integration package."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

_KDY_BLE_DIR = (
    Path(__file__).resolve().parents[2]
    / "custom_components"
    / "artsauna_ble"
    / "kdy_ble"
)
_PACKAGE = "kdy_ble_under_test"


def _ensure_package() -> ModuleType:
    if _PACKAGE not in sys.modules:
        pkg = ModuleType(_PACKAGE)
        pkg.__path__ = [str(_KDY_BLE_DIR)]  # type: ignore[attr-defined]
        sys.modules[_PACKAGE] = pkg
    return sys.modules[_PACKAGE]


def load_kdy_module(name: str) -> ModuleType:
    """Import ``kdy_ble.<name>`` from source without loading artsauna_ble.__init__."""
    _ensure_package()
    full_name = f"{_PACKAGE}.{name}"
    if full_name in sys.modules:
        return sys.modules[full_name]
    path = _KDY_BLE_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(full_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = module
    spec.loader.exec_module(module)
    return module
