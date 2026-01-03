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

import const
import utils


def validate(data: bytearray) -> bool:
    return sum(data[const.CHECKSUM_BYTES_SLICE]) % 256 == int(
        data[const.CHECKSUM_BYTE_POSITION]
    )


def target_temp(data: bytearray) -> int:
    return int(data[const.TARGET_TEMP_BYTE_POSITION])


def device_state(data: bytearray) -> str:
    return const.DEVICE_STATE_BYTES_MAP[int(data[const.DEVICE_STATE_BYTE_POSITION])]


def heating_state(data: bytearray) -> str:
    return const.HEATING_BYTES_MAP[int(data[const.HEATING_STATE_BYTE_POSITION])]


def time(data: bytearray) -> int:
    return int(data[const.TIME_BYTE_POSITION])


def current_temp(data: bytearray) -> int:
    return int(data[const.CURRENT_TEMP_BYTE_POSITION])


def unit(data: bytearray) -> str:
    return const.UNIT_BYTES_MAP[int(data[const.UNIT_BYTE_POSITION])]


def rgb_lighting(data: bytearray) -> str:
    internal_rgb = int(data[const.LIGHTING_BYTE_POSITION].to_bytes().hex()[1])
    return utils.external_rgb_to_color_led_label(
        utils.internal_to_external_rgb(internal_rgb)
    )


def lighting(data: bytearray) -> str:
    return const.LIGHTING_HEX_1_MAP[
        int(data[const.LIGHTING_BYTE_POSITION].to_bytes().hex()[0]) % 4
    ]


def is_light_on(data: bytearray) -> bool:
    return lighting(data) != "OFF" or rgb_lighting(data) != "OFF"


def volume(data: bytearray) -> int:
    return int(data[const.VOLUME_BYTE_POSITION])


def fm_frequency(data: bytearray) -> float:
    return int.from_bytes(data[const.FM_FREQUENCY_BYTES_SLICE]) / 100.0
