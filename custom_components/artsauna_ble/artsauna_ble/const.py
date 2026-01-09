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

from uuid import UUID

from bidict import bidict

CHARACTERISTIC_WRITE = UUID("0000ae01-0000-1000-8000-00805f9b34fb")
CHARACTERISTIC_NOTIFY = UUID("0000ae03-0000-1000-8000-00805f9b34fb")

CMD_APP_AUTH = b"\xff\xaa\x05ASOK3"
CMD_TOGGLE_POWER = b"\xff\xaa\x05ZG\x0e\x00\xb4"
CMD_TOGGLE_HEATING = b"\xff\xaa\x05ZG\x00\x02\xa8"
CMD_TEMP_UP = b"\xff\xaa\x05ZG\x06\x00\xac"
CMD_TEMP_DOWN = b"\xff\xaa\x05ZG\x00\x01\xa7"
CMD_VOLUME_PREFIX = b"\xff\xaa\x05ZG\r"
CMD_TIME_UP = b"\xff\xaa\x05ZG\x08\x00\xae"
CMD_TIME_DOWN = b"\xff\xaa\x05ZG\t\x00\xaf"
CMD_RGB_PREFIX = b"\xff\xaa\x05ZG\n\x00"
CMD_RGB_OFFSET = 175  # based on external rgb id; 0xaf
CMD_RGB_1 = b"\xff\xaa\x05ZG\n\x00\xb0"  # internal: 8
CMD_RGB_2 = b"\xff\xaa\x05ZG\n\x00\xb1"  # 0
CMD_RGB_3 = b"\xff\xaa\x05ZG\n\x00\xb2"  # 1
CMD_RGB_4 = b"\xff\xaa\x05ZG\n\x00\xb3"  # 2
CMD_RGB_5 = b"\xff\xaa\x05ZG\n\x00\xb4"  # 3
CMD_RGB_6 = b"\xff\xaa\x05ZG\n\x00\xb5"  # 4
CMD_RGB_7 = b"\xff\xaa\x05ZG\n\x00\xb6"  # 5
CMD_RGB_8 = b"\xff\xaa\x05ZG\n\x00\xb7"  # 6
CMD_RGB_9 = b"\xff\xaa\x05ZG\n\x00\xb8"  # 7
CMD_RGB_WHITE = CMD_RGB_1
CMD_RGB_GREEN = CMD_RGB_2
CMD_RGB_RED = CMD_RGB_3
CMD_RGB_BLUE = CMD_RGB_4
CMD_RGB_YELLOW = CMD_RGB_5
CMD_RGB_CYAN = CMD_RGB_6
CMD_RGB_PINK = CMD_RGB_7
CMD_RGB_OFF = CMD_RGB_8
CMD_RGB_RAINBOW = CMD_RGB_9
CMD_TOGGLE_EXTERNAL_LIGHT = b"\xff\xaa\x05ZG\x0b\x00\xb1"
CMD_TOGGLE_INTERNAL_LIGHT = b"\xff\xaa\x05ZG\x0b\x00\xb2"
CMD_TOGGLE_FM = b"\xff\xaa\x05ZG\x01\x00\xa7"
CMD_TOGGLE_BT = b"\xff\xaa\x05ZG\x02\x00\xa8"
CMD_TOGGLE_AUX = b"\xff\xaa\x05ZG\x04\x00\xaa"
CMD_TOGGLE_USB = b"\xff\xaa\x05ZG\x03\x00\xa9"
CMD_TOGGLE_UNIT = b"\xff\xaa\x05ZG\x05\x00\xab"

DEVICE_STATE_BYTE_POSITION = -9
HEATING_STATE_BYTE_POSITION = -8
CURRENT_TEMP_BYTE_POSITION = -7
TARGET_TEMP_BYTE_POSITION = -6
TIME_BYTE_POSITION = -5
UNIT_BYTE_POSITION = -4
VOLUME_BYTE_POSITION = -3
LIGHT_BYTE_POSITION = -2
CHECKSUM_BYTE_POSITION = -1
CHECKSUM_BYTES_SLICE = slice(-12, -1)
FM_FREQUENCY_BYTES_SLICE = slice(-2, None)

STATE_NOTIFICATION_START = b"\xff\xaa"
FM_NOTIFICATION_START = b"B\x02\x03\x00"

STATE_NOTIFICATION_REGEX = STATE_NOTIFICATION_START + b".{12}"
FM_NOTIFICATION_REGEX = FM_NOTIFICATION_START + b".{2}"

UNIT_BYTES_MAP = {0: "Celsius", 1: "Fahrenheit"}
DEVICE_STATE_BYTES_MAP = {5: "OFF", 4: "ON", 0: "RADIO", 1: "AUX/BT", 3: "USB"}
HEATING_BYTES_MAP = {0: "No Info", 1: "ON", 2: "OFF"}
LIGHTING_HEX_1_MAP = {
    0: "OFF",
    1: "External",
    2: "Internal",
    3: "External & Internal",
}

INTERNAL_RGB_COLOR_MAP = bidict(
    {
        "LED01: White": 8,
        "LED02: Green": 0,
        "LED03: Red": 1,
        "LED04: Blue": 2,
        "LED05: Yellow": 3,
        "LED06: Cyan": 4,
        "LED07: Pink": 5,
        "LED08: OFF": 6,
        "LED09: Rainbow": 7,
    }
)
