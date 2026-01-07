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

from __future__ import annotations

from dataclasses import dataclass

import const


@dataclass
class ArtsaunaState:
    """State of the Artsauna as communicated via BLE.

    Note:
        The artsauna internal values are used.
        It is the job of protocols using this dataclass to make sense of them.
    """

    state: int = 0
    heating_state: int = 0
    target_temp: int = 0
    current_temp: int = 0
    remaining_time: int = 0
    unit_is_celsius: int = 0
    volume: int = 0
    light: int = 0
    rgb: int = 0
    fm_frequency: int = 0

    @staticmethod
    def validate_ble_data(data: bytearray) -> bool:
        return sum(data[const.CHECKSUM_BYTES_SLICE]) % 256 == int(
            data[const.CHECKSUM_BYTE_POSITION]
        )

    @classmethod
    def from_ble_state_data(cls, data: bytearray) -> ArtsaunaState:
        return cls(
            state=int(data[const.DEVICE_STATE_BYTE_POSITION]),
            heating_state=int(data[const.HEATING_STATE_BYTE_POSITION]),
            target_temp=int(data[const.TARGET_TEMP_BYTE_POSITION]),
            current_temp=int(data[const.CURRENT_TEMP_BYTE_POSITION]),
            remaining_time=int(data[const.TIME_BYTE_POSITION]),
            unit_is_celsius=int(data[const.UNIT_BYTE_POSITION]),
            volume=int(data[const.VOLUME_BYTE_POSITION]),
            light=int(data[const.LIGHTING_BYTE_POSITION].to_bytes().hex()[0]) % 4,
            rgb=int(data[const.LIGHTING_BYTE_POSITION].to_bytes().hex()[1]),
            fm_frequency=int.from_bytes(data[const.FM_FREQUENCY_BYTES_SLICE]),
        )
