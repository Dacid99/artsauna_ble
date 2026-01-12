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

"""Data coordinator for receiving Artsauna updates."""

import logging
import time
from datetime import datetime

from homeassistant.core import CALLBACK_TYPE, HassJob, HomeAssistant, callback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .artsauna_ble import ArtsaunaBLEAdapter, ArtsaunaState
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

NEVER_TIME = -86400.0
DEBOUNCE_SECONDS = 1.0


class ArtsaunaBLECoordinator(DataUpdateCoordinator[None]):
    """Data coordinator for receiving Artsauna updates."""

    def __init__(self, hass: HomeAssistant, artsauna_ble: ArtsaunaBLEAdapter) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
        )
        self._artsauna_ble = artsauna_ble
        artsauna_ble.register_callback(self._async_handle_update)
        artsauna_ble.register_disconnected_callback(self._async_handle_disconnect)
        self.connected = False
        self._last_update_time = NEVER_TIME
        self._debounce_cancel: CALLBACK_TYPE | None = None
        self._debounced_update_job = HassJob(
            self._async_handle_debounced_update,
            f"LD2450 {artsauna_ble.address} BLE debounced update",
        )

    @callback
    def _async_handle_debounced_update(self, _now: datetime) -> None:
        """Handle debounced update."""
        self._debounce_cancel = None
        self._last_update_time = time.monotonic()
        self.async_set_updated_data(None)

    @callback
    def _async_handle_update(self, state: ArtsaunaState) -> None:
        """Just trigger the callbacks."""
        self.connected = True
        previous_last_updated_time = self._last_update_time
        self._last_update_time = time.monotonic()
        if self._last_update_time - previous_last_updated_time >= DEBOUNCE_SECONDS:
            self.async_set_updated_data(None)
            return
        if self._debounce_cancel is None:
            self._debounce_cancel = async_call_later(
                self.hass, DEBOUNCE_SECONDS, self._debounced_update_job
            )

    @callback
    def _async_handle_disconnect(self) -> None:
        """Trigger the callbacks for disconnected."""
        self.connected = False
        self.async_update_listeners()

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        if self._debounce_cancel is not None:
            self._debounce_cancel()
            self._debounce_cancel = None
        await super().async_shutdown()
