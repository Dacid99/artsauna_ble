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

"""The Artsauna-BLE integration models."""

from __future__ import annotations

from dataclasses import dataclass

from .artsauna_ble import ArtsaunaBLEAdapter
from .coordinator import ArtsaunaBLECoordinator


@dataclass
class ArtsaunaBLEData:
    """Data for the artsauna ble integration."""

    title: str
    device: ArtsaunaBLEAdapter
    coordinator: ArtsaunaBLECoordinator
