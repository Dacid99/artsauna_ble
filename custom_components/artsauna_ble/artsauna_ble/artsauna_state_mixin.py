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

from .models import ArtsaunaState


class ArtsaunaStateMixin:
    @property
    def state(self) -> ArtsaunaState:
        return self._state

    @property
    def rgb_mode(self) -> int:
        return self._state.rgb

    @property
    def volume(self) -> int:
        return self._state.volume

    @property
    def target_temp(self) -> int:
        return self._state.target_temp

    @property
    def current_temp(self) -> int:
        return self._state.current_temp

    @property
    def is_external_light_on(self) -> bool:
        return self._state.light % 2 == 1

    @property
    def is_internal_light_on(self) -> bool:
        return self._state.light > 2

    @property
    def is_rgb_on(self) -> bool:
        return self._state.rgb != 6

    @property
    def is_light_on(self) -> bool:
        return self.is_external_light_on or self.is_internal_light_on or self.is_rgb_on

    @property
    def fm_frequency(self) -> float:
        return self._state.fm_frequency / 100.0

    @property
    def is_power_on(self) -> bool:
        return self._state.state != 5

    @property
    def is_heating_on(self) -> bool:
        return self._state.heating_state == 1

    @property
    def remaining_time(self) -> int:
        return self._state.remaining_time

    @property
    def is_unit_celsius(self) -> bool:
        return self._state.unit_is_celsius == 0

    @property
    def is_aux_on(self) -> bool:
        return self._state.state == 2

    @property
    def is_fm_on(self) -> bool:
        return self._state.state == 0

    @property
    def is_usb_on(self) -> bool:
        return self._state.state == 3

    @property
    def is_bt_on(self) -> bool:
        return self._state.state == 1
