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

from .const import CMD_RGB_PREFIX, CMD_VOLUME_PREFIX


def construct_volume_cmd_data(volume: int) -> bytes:
    data = CMD_VOLUME_PREFIX + bytes([volume])
    data += bytes([sum(data[2:])])
    return data


def construct_rgb_cmd_data(rgb: int) -> bytes:
    data = CMD_RGB_PREFIX + bytes([rgb])
    data += bytes([sum(data[2:])])
    return data
