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

from functools import cached_property

from homeassistant.helpers.device_registry import format_mac


class ArtsaunaBLEDeviceMixin:
    @cached_property
    def address(self) -> str:
        """Return the address."""
        return format_mac(self._ble_device.address)

    @cached_property
    def name(self) -> str:
        """Get the name of the device."""
        return self._ble_device.name or self.address
