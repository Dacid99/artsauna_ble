"""Tests for device type classification (standalone const load)."""

import importlib.util
from pathlib import Path


def _load_integration_const():
    const_path = (
        Path(__file__).resolve().parents[2]
        / "custom_components"
        / "artsauna_ble"
        / "const.py"
    )
    spec = importlib.util.spec_from_file_location("artsauna_ble_const_ut2", const_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_device_type_for_kdy_name() -> None:
    const = _load_integration_const()
    assert const.device_type_for_name("KDYSauna-10") == const.DEVICE_TYPE_KDY


def test_device_type_for_artsauna_name() -> None:
    const = _load_integration_const()
    assert const.device_type_for_name("SAUNA-OSLO") == const.DEVICE_TYPE_ARTSAUNA
    assert const.device_type_for_name(None) == const.DEVICE_TYPE_ARTSAUNA
