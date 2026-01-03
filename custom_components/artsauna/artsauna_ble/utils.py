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


def construct_volume_cmd_data(volume: int) -> bytes:
    data = const.CMD_VOLUME_PREFIX + bytes([volume])
    data += bytes([sum(data[2:])])
    return data


def construct_rgb_cmd_data(rgb: int) -> bytes:
    data = const.CMD_RGB_PREFIX + bytes([rgb + const.CMD_RGB_OFFSET])
    return data


def internal_to_external_rgb(internal_rgb: int):
    return (internal_rgb - 2) % 9


def external_to_internal_rgb(external_rgb: int):
    return (external_rgb + 2) % 9


def external_rgb_to_color_led_label(external_rgb):
    return f"LED0{external_rgb}: {const.EXTERNAL_RGB_COLOR_MAP[external_rgb]}"
