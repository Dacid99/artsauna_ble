"""Stopping KDY must prevent pending commands from reconnecting."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.kdy.import_helper import load_kdy_module

load_kdy_module("const")
load_kdy_module("models")
adapter_mod = load_kdy_module("kdy_ble_adapter")


def make_device():
    return adapter_mod.KdyBLEAdapter(
        SimpleNamespace(address="AA:BB:CC:DD:EE:FF", name="KDYSauna-10")
    )


def make_client():
    client = MagicMock()
    client.is_connected = True
    client.start_notify = AsyncMock()
    client.stop_notify = AsyncMock()
    client.disconnect = AsyncMock()
    client.write_gatt_char = AsyncMock()
    return client


def test_pending_command_does_not_connect_after_stop():
    async def run():
        device = make_device()
        client = make_client()
        await device._ready_lock.acquire()
        with patch.object(
            adapter_mod,
            "establish_connection",
            new_callable=AsyncMock,
            return_value=client,
        ) as connect:
            command = asyncio.create_task(device.send_temp_up())
            await asyncio.sleep(0)
            stopping = asyncio.create_task(device.stop())
            await asyncio.sleep(0)
            device._ready_lock.release()
            with pytest.raises(adapter_mod.AdapterStoppedError):
                await command
            await stopping
            connect.assert_not_awaited()
            client.start_notify.assert_not_awaited()
            client.write_gatt_char.assert_not_awaited()
            assert device._client is None

    asyncio.run(run())


def test_stop_closes_connection_that_was_already_in_progress():
    async def run():
        device = make_device()
        client = make_client()
        connecting = asyncio.Event()
        finish_connect = asyncio.Event()

        async def establish(*args, **kwargs):
            connecting.set()
            await finish_connect.wait()
            return client

        with patch.object(adapter_mod, "establish_connection", side_effect=establish):
            command = asyncio.create_task(device.send_temp_up())
            await connecting.wait()
            stopping = asyncio.create_task(device.stop())
            await asyncio.sleep(0)
            finish_connect.set()
            with pytest.raises(adapter_mod.AdapterStoppedError):
                await command
            await stopping
            client.disconnect.assert_awaited_once()
            client.start_notify.assert_not_awaited()
            client.write_gatt_char.assert_not_awaited()
            assert device._client is None

    asyncio.run(run())


def test_command_waiting_for_operation_lock_is_rejected_after_stop():
    async def run():
        device = make_device()
        client = make_client()
        with patch.object(
            adapter_mod,
            "establish_connection",
            new_callable=AsyncMock,
            return_value=client,
        ) as connect:
            await device.initialise()
            await device._operation_lock.acquire()
            command = asyncio.create_task(device.send_temp_up())
            await asyncio.sleep(0)
            await device.stop()
            device._operation_lock.release()
            with pytest.raises(adapter_mod.AdapterStoppedError):
                await command
            assert connect.await_count == 1
            client.write_gatt_char.assert_not_awaited()

    asyncio.run(run())


def test_initialise_can_explicitly_restart_stopped_adapter():
    async def run():
        device = make_device()
        await device.stop()
        client = make_client()
        with patch.object(
            adapter_mod,
            "establish_connection",
            new_callable=AsyncMock,
            return_value=client,
        ):
            await device.initialise()
            await device.send_temp_up()
            client.write_gatt_char.assert_awaited_once()

    asyncio.run(run())


def test_stop_awaits_cancelled_reconnect_task():
    async def run():
        device = make_device()
        started = asyncio.Event()
        finished = asyncio.Event()

        async def reconnect():
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                await asyncio.sleep(0)
                finished.set()

        with patch.object(device, "_reconnect", side_effect=reconnect):
            device._schedule_reconnect()
            await started.wait()
            task = device._reconnect_task
            await device.stop()
            assert task.cancelled()
            assert finished.is_set()

    asyncio.run(run())
