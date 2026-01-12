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

from . import utils
from .const import (
    CMD_APP_AUTH,
    CMD_TEMP_DOWN,
    CMD_TEMP_UP,
    CMD_TIME_DOWN,
    CMD_TIME_UP,
    CMD_TOGGLE_AUX,
    CMD_TOGGLE_BT,
    CMD_TOGGLE_EXTERNAL_LIGHT,
    CMD_TOGGLE_FM,
    CMD_TOGGLE_HEATING,
    CMD_TOGGLE_INTERNAL_LIGHT,
    CMD_TOGGLE_POWER,
    CMD_TOGGLE_UNIT,
    CMD_TOGGLE_USB,
)


class ArtsaunaBLECommandMixin:
    async def send_auth(self):
        await self._send_command(CMD_APP_AUTH)

    async def send_toggle_power(self):
        await self._send_command(CMD_TOGGLE_POWER)

    async def send_toggle_heating(self):
        await self._send_command(CMD_TOGGLE_HEATING)

    async def send_temp_up(self):
        await self._send_command(CMD_TEMP_UP)

    async def send_temp_down(self):
        await self._send_command(CMD_TEMP_DOWN)

    async def send_time_up(self):
        await self._send_command(CMD_TIME_UP)

    async def send_time_down(self):
        await self._send_command(CMD_TIME_DOWN)

    async def send_toggle_internal_light(self):
        await self._send_command(CMD_TOGGLE_INTERNAL_LIGHT)

    async def send_toggle_external_light(self):
        await self._send_command(CMD_TOGGLE_EXTERNAL_LIGHT)

    async def send_toggle_unit(self):
        await self._send_command(CMD_TOGGLE_UNIT)

    async def send_toggle_fm(self):
        await self._send_command(CMD_TOGGLE_FM)

    async def send_toggle_bt(self):
        await self._send_command(CMD_TOGGLE_BT)

    async def send_toggle_aux(self):
        await self._send_command(CMD_TOGGLE_AUX)

    async def send_toggle_usb(self):
        await self._send_command(CMD_TOGGLE_USB)

    async def send_cycle_rgb(self):
        cmd_data = utils.construct_rgb_cmd_data(self._state.rgb)
        await self._send_command(cmd_data)

    async def send_set_rgb(self, rgb: int):
        cmd_data = utils.construct_rgb_cmd_data(rgb)
        await self._send_command(cmd_data)

    async def send_set_volume(self, volume: int):
        cmd_data = utils.construct_volume_cmd_data(volume)
        await self._send_command(cmd_data)
