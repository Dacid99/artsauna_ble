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

from . import const


@dataclass(frozen=True)
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
    def validate_ble_state_data(data: bytearray) -> bool:
        return sum(data[const.CHECKSUM_BYTES_SLICE]) % 256 == int(
            data[const.CHECKSUM_BYTE_POSITION]
        )

    def new_from_ble_state_data(self, ble_state_data: bytearray) -> ArtsaunaState:
        return ArtsaunaState(
            state=int(ble_state_data[const.DEVICE_STATE_BYTE_POSITION]),
            heating_state=int(ble_state_data[const.HEATING_STATE_BYTE_POSITION]),
            target_temp=int(ble_state_data[const.TARGET_TEMP_BYTE_POSITION]),
            current_temp=int(ble_state_data[const.CURRENT_TEMP_BYTE_POSITION]),
            remaining_time=int(ble_state_data[const.TIME_BYTE_POSITION]),
            unit_is_celsius=int(ble_state_data[const.UNIT_BYTE_POSITION]),
            volume=int(ble_state_data[const.VOLUME_BYTE_POSITION]),
            light=int(ble_state_data[const.LIGHT_BYTE_POSITION].to_bytes().hex()[0])
            % 4,
            rgb=int(ble_state_data[const.LIGHT_BYTE_POSITION].to_bytes().hex()[1]),
            fm_frequency=self.fm_frequency,
        )

    def new_from_ble_fm_data(self, ble_fm_data: bytearray) -> ArtsaunaState:
        return ArtsaunaState(
            state=self.state,
            heating_state=self.heating_state,
            target_temp=self.target_temp,
            current_temp=self.current_temp,
            remaining_time=self.remaining_time,
            unit_is_celsius=self.unit_is_celsius,
            volume=self.volume,
            light=self.light,
            rgb=self.rgb,
            fm_frequency=int.from_bytes(ble_fm_data[const.FM_FREQUENCY_BYTES_SLICE]),
        )
