"""KDY notification reassembly across channels and connection boundaries."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.kdy.import_helper import load_kdy_module

const = load_kdy_module("const")
load_kdy_module("models")
adapter_mod = load_kdy_module("kdy_ble_adapter")
STATUS = bytes.fromhex("AA0130302023000000000000000000000100000000CC")
POWER_OFF_STATUS = STATUS[:1] + b"\x00" + STATUS[2:]


@pytest.fixture
def device():
    return adapter_mod.KdyBLEAdapter(
        SimpleNamespace(address="AA:BB:CC:DD:EE:FF", name="KDYSauna-10")
    )


def notify(device, data, channel=const.CHARACTERISTIC_FFF2):
    device._notification_handler(SimpleNamespace(uuid=channel), bytearray(data))


@pytest.mark.parametrize("channel", [const.CHARACTERISTIC_FFF1, const.CHARACTERISTIC_FFF2])
@pytest.mark.parametrize("split", range(1, len(STATUS)))
def test_fragmented_status(device, channel, split):
    received = []
    device.register_callback(received.append)
    notify(device, STATUS[:split], channel)
    assert received == []
    notify(device, STATUS[split:], channel)
    assert [state.raw for state in received] == [STATUS]


def test_multiple_frames_and_partial_tail(device):
    received = []
    device.register_callback(received.append)
    notify(device, STATUS + POWER_OFF_STATUS + STATUS[:10])
    assert [state.raw for state in received] == [STATUS, POWER_OFF_STATUS]
    notify(device, STATUS[10:])
    assert [state.raw for state in received] == [STATUS, POWER_OFF_STATUS, STATUS]


def test_interleaved_channels_do_not_mix_fragments(device):
    received = []
    device.register_callback(received.append)
    notify(device, STATUS[:8], const.CHARACTERISTIC_FFF1)
    notify(device, POWER_OFF_STATUS[:15], const.CHARACTERISTIC_FFF2)
    notify(device, STATUS[8:], const.CHARACTERISTIC_FFF1)
    notify(device, POWER_OFF_STATUS[15:], const.CHARACTERISTIC_FFF2)
    assert [state.raw for state in received] == [STATUS, POWER_OFF_STATUS]


def test_noise_and_invalid_frames_resynchronize(device):
    received = []
    device.register_callback(received.append)
    notify(device, b"noise" + STATUS[:-1] + b"\x00" + b"\xaa" + STATUS)
    assert [state.raw for state in received] == [STATUS]


def test_payload_can_contain_start_and_end_bytes(device):
    payload = bytearray(STATUS)
    payload[9:11] = b"\xaa\xcc"
    notify(device, payload[:10])
    notify(device, payload[10:])
    assert device.state.raw == bytes(payload)


def test_noise_does_not_accumulate(device):
    for _ in range(100):
        notify(device, b"\xaa" * 200)
    buffer = device._notification_buffers[const.CHARACTERISTIC_FFF2]
    assert len(buffer) < const.STATUS_PACKET_LENGTH
    notify(device, b"\x00" * 200)
    assert not buffer


def test_empty_and_unknown_notifications_are_ignored(device):
    received = []
    device.register_callback(received.append)
    notify(device, b"")
    notify(device, STATUS, "unknown")
    assert received == []
    assert all(not buffer for buffer in device._notification_buffers.values())


@pytest.mark.parametrize("expected_disconnect", [True, False])
def test_disconnect_discards_fragments(device, expected_disconnect):
    async def run():
        received = []
        device.register_callback(received.append)
        for channel in (const.CHARACTERISTIC_FFF1, const.CHARACTERISTIC_FFF2):
            notify(device, STATUS[:10], channel)
        device._expected_disconnect = expected_disconnect
        with patch.object(device, "_reconnect", new_callable=AsyncMock) as reconnect:
            device._disconnected(MagicMock())
            await asyncio.sleep(0)
            assert reconnect.await_count == (0 if expected_disconnect else 1)
        assert all(not buffer for buffer in device._notification_buffers.values())
        notify(device, STATUS[10:])
        assert received == []
        notify(device, STATUS)
        assert [state.raw for state in received] == [STATUS]

    asyncio.run(run())


def test_command_disconnect_discards_fragments_without_callback(device):
    notify(device, STATUS[:10])
    asyncio.run(device._execute_disconnect())
    assert all(not buffer for buffer in device._notification_buffers.values())


def test_new_connection_discards_fragments(device):
    async def run():
        notify(device, STATUS[:10])
        with patch.object(adapter_mod, "establish_connection", new_callable=AsyncMock):
            await device._ensure_connected()
        assert all(not buffer for buffer in device._notification_buffers.values())

    asyncio.run(run())


async def subscribe(device):
    """Capture the actual callbacks installed on a connected client."""
    client = MagicMock()
    client.is_connected = True
    client.start_notify = AsyncMock()
    client.stop_notify = AsyncMock()
    client.disconnect = AsyncMock()
    device._client = client
    await device._start_notifications()
    callbacks = {call.args[0]: call.args[1] for call in client.start_notify.await_args_list}
    return client, callbacks


@pytest.mark.parametrize("channel", [const.CHARACTERISTIC_FFF1, const.CHARACTERISTIC_FFF2])
@pytest.mark.parametrize("explicit_disconnect", [True, False])
@pytest.mark.parametrize("reconnect", [True, False])
def test_late_notifications_are_ignored(device, channel, explicit_disconnect, reconnect):
    async def run():
        received = []
        device.register_callback(received.append)
        client, callbacks = await subscribe(device)
        characteristic = SimpleNamespace(uuid=channel)
        old_callback = callbacks[channel]
        old_callback(characteristic, bytearray(STATUS[:10]))

        if explicit_disconnect:
            # Model notifications queued while stop_notify is still running.
            async def stop_notify(_channel):
                old_callback(characteristic, bytearray(STATUS))
                old_callback(characteristic, bytearray(STATUS[:10]))
            client.stop_notify.side_effect = stop_notify
            await device._execute_disconnect()
        else:
            with patch.object(device, "_reconnect", new_callable=AsyncMock):
                device._disconnected(client)
                await asyncio.sleep(0)

        if reconnect:
            _, new_callbacks = await subscribe(device)
            new_callback = new_callbacks[channel]
            new_callback(characteristic, bytearray(POWER_OFF_STATUS[:10]))
            # An old disconnect callback must not invalidate the new session.
            device._disconnected(client)

        # Old callbacks must neither publish states nor contaminate fragments.
        old_callback(characteristic, bytearray(STATUS))
        old_callback(characteristic, bytearray(STATUS[:10]))
        assert received == []
        if reconnect:
            new_callback(characteristic, bytearray(POWER_OFF_STATUS[10:]))
            assert [state.raw for state in received] == [POWER_OFF_STATUS]
        else:
            assert all(not buffer for buffer in device._notification_buffers.values())
            assert device.state.raw == b""

    asyncio.run(run())


def test_notifications_from_disconnected_client_are_ignored(device):
    async def run():
        received = []
        device.register_callback(received.append)
        client, callbacks = await subscribe(device)
        client.is_connected = False
        callback = callbacks[const.CHARACTERISTIC_FFF2]
        characteristic = SimpleNamespace(uuid=const.CHARACTERISTIC_FFF2)
        callback(characteristic, bytearray(STATUS))
        callback(characteristic, bytearray(STATUS[:10]))
        assert received == []
        assert all(not buffer for buffer in device._notification_buffers.values())

    asyncio.run(run())


def test_resubscribe_invalidates_previous_callback_on_same_client(device):
    async def run():
        received = []
        device.register_callback(received.append)
        client, callbacks = await subscribe(device)
        characteristic = SimpleNamespace(uuid=const.CHARACTERISTIC_FFF2)
        callbacks[const.CHARACTERISTIC_FFF2](characteristic, bytearray(STATUS[:10]))
        await device._start_notifications()
        assert all(not buffer for buffer in device._notification_buffers.values())
        callbacks[const.CHARACTERISTIC_FFF2](characteristic, bytearray(STATUS))
        assert received == []
        new_callback = client.start_notify.await_args_list[-2].args[1]
        new_callback(characteristic, bytearray(POWER_OFF_STATUS))
        assert [state.raw for state in received] == [POWER_OFF_STATUS]

    asyncio.run(run())
