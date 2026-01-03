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


@dataclass(frozen=True)
class ArtsaunaState:
    """State of the Artsauna as communicated via BLE.

    Note:
        The artsauna internal values are used.
        It is the job of protocols using this dataclass to make sense of them.
    """

    power_on: bool = False
    heating_on: int = 0
    target_temp: int = 0
    current_temp: int = 0
    remaining_time: int = 0
    volume: int = 0
    lighting: int = 0
    rgb: int = 0
    fm_frequency: int = 0
    unit_is_celsius: bool = True

    def update_from_data(self, data: bytes) -> None:
