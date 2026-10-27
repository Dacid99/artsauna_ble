"""Regression tests for protocol selection and existing Artsauna entries."""

import asyncio
import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import CONF_ADDRESS, CONF_DEVICE_CLASS


@pytest.fixture
def integration():
    """Load the integration with Bluetooth and protocol adapters isolated."""
    package = "artsauna_device_type_under_test"
    root = Path(__file__).resolve().parents[2] / "custom_components/artsauna_ble"
    bluetooth = MagicMock()
    bluetooth.BluetoothServiceInfoBleak = type("BluetoothServiceInfoBleak", (), {})
    match = ModuleType("homeassistant.components.bluetooth.match")
    match.ADDRESS = "address"
    match.BluetoothCallbackMatcher = dict

    artsauna_adapter = MagicMock(name="ArtsaunaBLEAdapter")
    kdy_adapter = MagicMock(name="KdyBLEAdapter")
    for adapter in (artsauna_adapter, kdy_adapter):
        adapter.return_value.initialise = AsyncMock()
        adapter.return_value.stop = AsyncMock()

    def module(name, **attrs):
        result = ModuleType(name)
        result.__dict__.update(attrs)
        return result

    modules = {
        "homeassistant.components.bluetooth": bluetooth,
        "homeassistant.components.bluetooth.match": match,
        f"{package}.artsauna_ble": module("artsauna_ble", ArtsaunaBLEAdapter=artsauna_adapter),
        f"{package}.kdy_ble": module("kdy_ble", KdyBLEAdapter=kdy_adapter),
        f"{package}.coordinator": module("coordinator", ArtsaunaBLECoordinator=MagicMock()),
        f"{package}.models": module("models", ArtsaunaBLEData=MagicMock()),
    }
    spec = importlib.util.spec_from_file_location(
        package, root / "__init__.py", submodule_search_locations=[str(root)]
    )
    loaded = importlib.util.module_from_spec(spec)
    modules[package] = loaded
    with patch.dict(sys.modules, modules), patch(
        "homeassistant.components.bluetooth", bluetooth, create=True
    ):
        spec.loader.exec_module(loaded)
        loaded.close_stale_connections_by_address = AsyncMock()
        yield loaded, artsauna_adapter, kdy_adapter


@pytest.mark.parametrize(
    ("stored_type", "expected_adapter"),
    [("artsauna", 1), ("ARTSAUNA", 1), ("kdy", 2)],
)
def test_adapter_selection(integration, stored_type, expected_adapter):
    """Stored protocol strings select the intended adapter."""
    assert integration[0].get_adapter_class(stored_type) is integration[expected_adapter]


def test_unknown_device_type_is_rejected(integration):
    with pytest.raises(ValueError):
        integration[0].get_adapter_class("unknown")


@pytest.mark.parametrize("stored_type", [None, "artsauna", "ARTSAUNA", "kdy"])
def test_setup_entry_protocol(integration, stored_type):
    """Old address-only entries still load using the Artsauna adapter."""
    loaded, artsauna_adapter, kdy_adapter = integration
    address = "AA:BB:CC:DD:EE:FF"
    data = {CONF_ADDRESS: address}
    if stored_type is not None:
        data[CONF_DEVICE_CLASS] = stored_type
    entry = MagicMock(data=data, entry_id="existing-entry", title="Existing sauna")
    hass = SimpleNamespace(
        data={},
        config_entries=SimpleNamespace(async_forward_entry_setups=AsyncMock()),
        bus=MagicMock(),
    )

    assert asyncio.run(loaded.async_setup_entry(hass, entry)) is True

    expected = kdy_adapter if stored_type == "kdy" else artsauna_adapter
    other = artsauna_adapter if stored_type == "kdy" else kdy_adapter
    expected.assert_called_once()
    expected.return_value.initialise.assert_awaited_once()
    other.assert_not_called()
    # Loading existing entries must preserve their stored data and identity.
    assert entry.data == data
    assert "existing-entry" in hass.data[loaded.HASS_DOMAIN]


@pytest.mark.parametrize("device_type", ["artsauna", "kdy"])
def test_config_flow_stores_selected_protocol(integration, device_type):
    """The selector values survive creation and choose the correct adapter."""
    loaded, artsauna_adapter, kdy_adapter = integration
    flow_module = __import__(f"{loaded.__name__}.config_flow", fromlist=["*"])
    flow = flow_module.ArtsaunaBLEConfigFlow()
    flow.hass = MagicMock()
    address = "AA:BB:CC:DD:EE:FF"
    discovery = SimpleNamespace(address=address, name="Sauna", device=MagicMock())
    flow._discovered_devices[address] = discovery
    flow._discovery_info = discovery
    flow.async_show_form = MagicMock()
    flow.async_set_unique_id = AsyncMock()
    flow._abort_if_unique_id_configured = MagicMock()
    flow.async_create_entry = MagicMock()

    asyncio.run(flow.async_step_user())
    schema = flow.async_show_form.call_args.kwargs["data_schema"]
    user_input = {CONF_ADDRESS: address, CONF_DEVICE_CLASS: device_type}
    assert schema(user_input) == user_input
    selector = next(
        value for key, value in schema.schema.items()
        if key.schema == CONF_DEVICE_CLASS
    )
    assert selector.config["options"] == [
        {"value": "artsauna", "label": "ARTSAUNA"},
        {"value": "kdy", "label": "KDY"},
    ]

    asyncio.run(flow.async_step_user(user_input))

    flow.async_create_entry.assert_called_once_with(title="Sauna", data=user_input)
    expected = kdy_adapter if device_type == "kdy" else artsauna_adapter
    expected.assert_called_once_with(discovery.device)
    expected.return_value.stop.assert_awaited_once()
