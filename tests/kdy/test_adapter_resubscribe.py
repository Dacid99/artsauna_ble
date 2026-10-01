"""Regression: command retry after error must resubscribe notifications."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from tests.kdy.import_helper import load_kdy_module

load_kdy_module("const")
load_kdy_module("models")
adapter_mod = load_kdy_module("kdy_ble_adapter")
KdyBLEAdapter = adapter_mod.KdyBLEAdapter
CHARACTERISTIC_FFF2 = load_kdy_module("const").CHARACTERISTIC_FFF2


def _make_client() -> MagicMock:
    client = MagicMock()
    client.is_connected = True
    client.start_notify = AsyncMock()
    client.stop_notify = AsyncMock()
    client.write_gatt_char = AsyncMock()
    client.disconnect = AsyncMock()
    return client


def test_send_command_resubscribes_after_error_disconnect() -> None:
    """After _execute_disconnect, the next command must call start_notify again."""

    async def _run() -> None:
        ble_device = MagicMock()
        ble_device.address = "AA:BB:CC:DD:EE:FF"
        ble_device.name = "KDYSauna-10"

        first_client = _make_client()
        second_client = _make_client()
        clients = iter([first_client, second_client])

        async def establish(*_args, **_kwargs):
            return next(clients)

        with patch.object(adapter_mod, "establish_connection", side_effect=establish):
            with patch.object(adapter_mod, "DEFAULT_ATTEMPTS", 1):
                device = KdyBLEAdapter(ble_device)
                await device.initialise()

                assert first_client.start_notify.await_count >= 1
                first_client.start_notify.reset_mock()

                # Simulate the error-recovery disconnect used by _send_command_locked
                await device._execute_disconnect()
                assert device._client is None

                await device._send_command(1, 1)

                # Reconnected client must be subscribed for status updates
                second_client.start_notify.assert_any_await(
                    CHARACTERISTIC_FFF2, device._notification_handler
                )
                second_client.write_gatt_char.assert_awaited()

    asyncio.run(_run())
