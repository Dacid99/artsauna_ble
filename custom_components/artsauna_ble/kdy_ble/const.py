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

"""KDY Sauna BLE constants."""

from __future__ import annotations

SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_FFF1 = "0000fff1-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_FFF2 = "0000fff2-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_FFF3 = "0000fff3-0000-1000-8000-00805f9b34fb"

DEVICE_NAME_PREFIXES = ("KDYSauna",)

STATUS_PACKET_LENGTH = 22
STATUS_START = 0xAA
STATUS_END = 0xCC

OFFSET_POWER = 1
OFFSET_REMAINING_MINUTES = 2
OFFSET_CURRENT_TEMP = 4
OFFSET_TARGET_TEMP = 5
OFFSET_VOLUME = 13
OFFSET_FM_ON = 14
OFFSET_BT_ON = 15
OFFSET_USB_ON = 16
OFFSET_UNIT_FAHRENHEIT = 18

COMMAND_PACKET_LENGTH = 22
COMMAND_START = 0xAA
COMMAND_END = 0xCC

CMD_BYTE_POWER = 1
CMD_BYTE_TIMER = 3
CMD_BYTE_TARGET_TEMP = 5
CMD_BYTE_OUTSIDE_LIGHT = 6
CMD_BYTE_INSIDE_LIGHT = 7
CMD_BYTE_RGB = 8
CMD_BYTE_VOLUME = 13
CMD_BYTE_FM = 14
CMD_BYTE_BT = 15
CMD_BYTE_USB = 16
CMD_BYTE_UNIT = 18

CMD_VALUE_TOGGLE = 1
CMD_VALUE_STEP_UP = 1
CMD_VALUE_STEP_DOWN = 2
