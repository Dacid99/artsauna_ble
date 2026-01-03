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


async def send_ble_cmd(artsauna_client, cmd_data):
    return await artsauna_client.write_gatt_char(
        const.CHARACTERISTIC_WRITE, data=cmd_data
    )


async def set_app_mode(artsauna_client):
    return await send_ble_cmd(artsauna_client, const.CMD_APP_AUTH)


async def toggle_unit(artsauna_client):
    return await send_ble_cmd(artsauna_client, const.CMD_TOGGLE_UNIT)


async def increase_time(artsauna_client):
    return await send_ble_cmd(artsauna_client, const.CMD_TIME_UP)


async def decrease_time(artsauna_client):
    return await send_ble_cmd(artsauna_client, const.CMD_TIME_DOWN)


async def increase_target_temp(artsauna_client):
    return await send_ble_cmd(artsauna_client, const.CMD_TEMP_UP)


async def decrease_target_temp(artsauna_client):
    return await send_ble_cmd(artsauna_client, const.CMD_TEMP_DOWN)


async def set_volume(artsauna_client, volume: int):
    cmd_data = utils.construct_volume_cmd_data(volume)
    return await send_ble_cmd(artsauna_client, cmd_data)


async def set_rgb(artsauna_client, rgb: int):
    # using external rgb id
    cmd_data = utils.construct_rgb_cmd_data(rgb)
    return await send_ble_cmd(artsauna_client, cmd_data)


async def toggle_external_lighting(artsauna_client):
    return await send_ble_cmd(artsauna_client, const.CMD_TOGGLE_EXTERNAL_LIGHT)


async def toggle_internal_lighting(artsauna_client):
    return await send_ble_cmd(artsauna_client, const.CMD_TOGGLE_INTERNAL_LIGHT)


async def toggle_fm(artsauna_client):
    return await send_ble_cmd(artsauna_client, const.CMD_TOGGLE_FM)


async def toggle_bt(artsauna_client):
    return await send_ble_cmd(artsauna_client, const.CMD_TOGGLE_BT)


async def toggle_usb(artsauna_client):
    return await send_ble_cmd(artsauna_client, const.CMD_TOGGLE_USB)


async def toggle_aux(artsauna_client):
    return await send_ble_cmd(artsauna_client, const.CMD_TOGGLE_AUX)


async def toggle_power(artsauna_client):
    return await send_ble_cmd(artsauna_client, const.CMD_TOGGLE_POWER)


async def toggle_heating(artsauna_client):
    return await send_ble_cmd(artsauna_client, const.CMD_TOGGLE_HEATING)
