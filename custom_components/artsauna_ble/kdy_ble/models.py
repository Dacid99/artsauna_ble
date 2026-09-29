# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Artsauna-BLE - integration for Home Assistant
# Copyright (C) 2025 David & Philipp Aderbauer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""KDY Sauna BLE state model.

Only hardware-verified / high-confidence observed fields are decoded.
Unknown bytes remain in ``raw`` and are never assigned meaning.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .const import (
    COMMAND_END,
    COMMAND_PACKET_LENGTH,
    COMMAND_START,
    OFFSET_BT_ON,
    OFFSET_CURRENT_TEMP,
    OFFSET_FM_ON,
    OFFSET_POWER,
    OFFSET_REMAINING_MINUTES,
    OFFSET_TARGET_TEMP,
    OFFSET_UNIT_FAHRENHEIT,
    OFFSET_USB_ON,
    OFFSET_VOLUME,
    STATUS_END,
    STATUS_PACKET_LENGTH,
    STATUS_START,
)


class InvalidStatusPacket(ValueError):
    """Raised when a payload is not a valid 22-byte AA…CC status frame."""


def build_command_packet(byte_index: int, value: int) -> bytes:
    """Build a 22-byte AA…CC command packet with exactly one byte set.

    Mirrors the decompiled app's ``d(byte value, int index)`` write helper:
    all bytes zero except framing and the single target byte.
    """
    if not 1 <= byte_index <= COMMAND_PACKET_LENGTH - 2:
        raise ValueError(f"byte_index {byte_index} out of range")
    if not 0 <= value <= 0xFF:
        raise ValueError(f"value {value} out of range")

    packet = bytearray(COMMAND_PACKET_LENGTH)
    packet[0] = COMMAND_START
    packet[byte_index] = value
    packet[-1] = COMMAND_END
    return bytes(packet)


@dataclass(frozen=True)
class KdyState:
    """Decoded KDY status.

    Bytes 6–12, 19–20 are intentionally not exposed as named fields (unknown).
    See PROTOCOL.md status frame table for per-field confidence.
    """

    power: bool = False  # byte 1
    remaining_minutes: int = 0  # bytes 2–3
    current_temp: int = 0  # byte 4 (°C)
    target_temp: int = 0  # byte 5 (°C)
    volume: int = 0  # byte 13
    fm_on: bool = False  # byte 14
    bt_on: bool = False  # byte 15
    usb_on: bool = False  # byte 16
    unit_fahrenheit: bool = False  # byte 18
    raw: bytes = field(default_factory=bytes)  # full notification payload

    @staticmethod
    def is_status_frame(data: bytes | bytearray) -> bool:
        """Return True if data looks like a verified AA…CC status frame."""
        return (
            len(data) == STATUS_PACKET_LENGTH
            and data[0] == STATUS_START
            and data[-1] == STATUS_END
        )

    @classmethod
    def from_ble_status(cls, data: bytes | bytearray) -> KdyState:
        """Parse known fields from a status notification.

        Raises InvalidStatusPacket if framing is not verified AA…CC / 22 bytes.
        """
        payload = bytes(data)
        if not cls.is_status_frame(payload):
            raise InvalidStatusPacket(
                f"Expected {STATUS_PACKET_LENGTH}-byte AA…CC frame, "
                f"got len={len(payload)} hex={payload.hex()}"
            )

        # observed: bytes 2 and 3 both carry remaining minutes and match
        remaining = payload[OFFSET_REMAINING_MINUTES]

        return cls(
            power=payload[OFFSET_POWER] != 0,
            remaining_minutes=remaining,
            current_temp=payload[OFFSET_CURRENT_TEMP],
            target_temp=payload[OFFSET_TARGET_TEMP],
            volume=payload[OFFSET_VOLUME],
            fm_on=payload[OFFSET_FM_ON] != 0,
            bt_on=payload[OFFSET_BT_ON] != 0,
            usb_on=payload[OFFSET_USB_ON] != 0,
            unit_fahrenheit=payload[OFFSET_UNIT_FAHRENHEIT] != 0,
            raw=payload,
        )

    def format_known_fields(self) -> str:
        """Human-readable known fields for debug logs."""
        return (
            f"Power: {'ON' if self.power else 'OFF'}; "
            f"Remaining: {self.remaining_minutes} min; "
            f"Current: {self.current_temp} °C; "
            f"Target: {self.target_temp} °C; "
            f"Volume: {self.volume}; "
            f"FM: {'ON' if self.fm_on else 'OFF'}; "
            f"BT: {'ON' if self.bt_on else 'OFF'}; "
            f"USB: {'ON' if self.usb_on else 'OFF'}; "
            f"Unit: {'F' if self.unit_fahrenheit else 'C'}; "
            f"Light/RGB: unknown"
        )
