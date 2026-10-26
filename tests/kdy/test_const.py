"""Tests for KDY BLE protocol constants."""

from tests.kdy.import_helper import load_kdy_module

const = load_kdy_module("const")


def test_service_and_characteristic_uuids() -> None:
    assert const.SERVICE_UUID == "0000fff0-0000-1000-8000-00805f9b34fb"
    assert const.CHARACTERISTIC_FFF1 == "0000fff1-0000-1000-8000-00805f9b34fb"
    assert const.CHARACTERISTIC_FFF2 == "0000fff2-0000-1000-8000-00805f9b34fb"
    assert const.CHARACTERISTIC_FFF3 == "0000fff3-0000-1000-8000-00805f9b34fb"


def test_command_frame_constants() -> None:
    assert const.COMMAND_PACKET_LENGTH == 22
    assert const.COMMAND_START == 0xAA
    assert const.COMMAND_END == 0xCC


def test_command_byte_indices_are_within_payload() -> None:
    indices = [
        const.CMD_BYTE_POWER,
        const.CMD_BYTE_TIMER,
        const.CMD_BYTE_TARGET_TEMP,
        const.CMD_BYTE_OUTSIDE_LIGHT,
        const.CMD_BYTE_INSIDE_LIGHT,
        const.CMD_BYTE_RGB,
        const.CMD_BYTE_VOLUME,
        const.CMD_BYTE_FM,
        const.CMD_BYTE_BT,
        const.CMD_BYTE_USB,
        const.CMD_BYTE_UNIT,
    ]
    assert all(1 <= index <= const.COMMAND_PACKET_LENGTH - 2 for index in indices)
