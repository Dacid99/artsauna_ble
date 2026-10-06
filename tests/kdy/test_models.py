"""Tests for KDY status parsing — only real captured payloads."""

import pytest

from tests.kdy.import_helper import load_kdy_module

load_kdy_module("const")  # models imports .const
models = load_kdy_module("models")
KdyState = models.KdyState
InvalidStatusPacket = models.InvalidStatusPacket
build_command_packet = models.build_command_packet

# Real hardware capture from KDYSauna-10 (Artsauna_KDYSauna10_BLE-Protokoll.md):
# power ON, 48 min remaining, 32 °C actual, 35 °C target
CAPTURED_STATUS = bytes.fromhex("AA0130302023000000000000000000000100000000CC")


def test_parse_captured_status() -> None:
    state = KdyState.from_ble_status(CAPTURED_STATUS)

    assert state.power is True
    assert state.remaining_minutes == 0x30  # 48 minutes
    assert state.current_temp == 0x20  # 32 °C
    assert state.target_temp == 0x23  # 35 °C
    assert state.raw == CAPTURED_STATUS


def test_raw_payload_retained() -> None:
    state = KdyState.from_ble_status(CAPTURED_STATUS)
    assert state.raw.hex() == CAPTURED_STATUS.hex()


def test_is_status_frame() -> None:
    assert KdyState.is_status_frame(CAPTURED_STATUS) is True
    assert KdyState.is_status_frame(b"\xaa\x00") is False
    assert KdyState.is_status_frame(bytes(22)) is False


def test_invalid_frame_raises() -> None:
    with pytest.raises(InvalidStatusPacket):
        KdyState.from_ble_status(b"\xff\xaa\x05ASOK3")


def test_power_off_observed_values() -> None:
    """Power OFF uses observed byte-1 value 0x00; other fields from same framing."""
    payload = bytearray(CAPTURED_STATUS)
    payload[1] = 0x00
    state = KdyState.from_ble_status(payload)
    assert state.power is False
    assert state.raw == bytes(payload)


def test_format_known_fields() -> None:
    state = KdyState.from_ble_status(CAPTURED_STATUS)
    text = state.format_known_fields()
    assert "ON" in text
    assert "48" in text
    assert "USB: ON" in text
    assert "Unit: C" in text


def test_parse_captured_status_decodes_audio_and_unit_fields() -> None:
    state = KdyState.from_ble_status(CAPTURED_STATUS)

    assert state.volume == 0
    assert state.fm_on is False
    assert state.bt_on is False
    assert state.usb_on is True  # byte 16 == 0x01 in this capture
    assert state.unit_fahrenheit is False


def test_build_command_packet_sets_single_byte() -> None:
    packet = build_command_packet(1, 1)

    assert len(packet) == 22
    assert packet[0] == 0xAA
    assert packet[-1] == 0xCC
    assert packet[1] == 1
    assert all(b == 0 for i, b in enumerate(packet) if i not in (0, 1, 21))


def test_build_command_packet_volume_absolute_value() -> None:
    packet = build_command_packet(13, 20)

    assert packet[13] == 20
    assert packet.hex() == build_command_packet(13, 20).hex()


def test_build_command_packet_rejects_out_of_range_index() -> None:
    with pytest.raises(ValueError):
        build_command_packet(0, 1)
    with pytest.raises(ValueError):
        build_command_packet(21, 1)


def test_build_command_packet_rejects_out_of_range_value() -> None:
    with pytest.raises(ValueError):
        build_command_packet(1, -1)
    with pytest.raises(ValueError):
        build_command_packet(1, 256)
