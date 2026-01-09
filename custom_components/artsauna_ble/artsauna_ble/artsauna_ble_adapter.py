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

import asyncio
import logging
import re
import sys
from collections.abc import Callable

from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from bleak.exc import BleakDBusError, BleakError
from bleak_retry_connector import (
    BLEAK_RETRY_EXCEPTIONS,
    BleakClientWithServiceCache,
    BleakNotFoundError,
    establish_connection,
    retry_bluetooth_connection_error,
)

from .artsauna_ble_device_mixin import ArtsaunaBLEDeviceMixin
from .artsauna_command_mixin import (
    ArtsaunaBLECommandMixin,
)
from .artsauna_state_mixin import ArtsaunaStateMixin
from .const import (
    CHARACTERISTIC_NOTIFY,
    CHARACTERISTIC_WRITE,
    FM_NOTIFICATION_REGEX,
    STATE_NOTIFICATION_REGEX,
)
from .models import ArtsaunaState

_LOGGER = logging.getLogger(__name__)
DEFAULT_ATTEMPTS = sys.maxsize
BLEAK_BACKOFF_TIME = 0.25


class ArtsaunaBLEAdapter(
    ArtsaunaStateMixin, ArtsaunaBLEDeviceMixin, ArtsaunaBLECommandMixin
):
    def __init__(self, ble_device: BLEDevice) -> None:
        self._ble_device = ble_device
        self._state = ArtsaunaState()
        self._client: BleakClientWithServiceCache | None = None
        self._notification_buffer = b""
        self._operation_lock = asyncio.Lock()
        self._connect_lock = asyncio.Lock()
        self._callbacks: list[Callable[[ArtsaunaState], None]] = []
        self._disconnected_callbacks: list[Callable[[], None]] = []
        self._expected_disconnect = False

    async def initialise(self) -> None:
        await self._ensure_connected()

        _LOGGER.debug("%s: Subscribe to notifications", self.name)
        if self._client is not None:
            _LOGGER.debug(self._client)

            _LOGGER.debug("Sending auth commands")
            await self.send_auth()
            await asyncio.sleep(0.1)

            await self._client.start_notify(
                CHARACTERISTIC_NOTIFY, self._notification_handler
            )
        else:
            _LOGGER.debug("Client is unexpectedly None")

    def set_ble_device_and_advertisement_data(
        self, ble_device: BLEDevice, advertisement_data: AdvertisementData
    ) -> None:
        """Set the ble device."""
        self._ble_device = ble_device
        self._advertisement_data = advertisement_data

    def _notification_handler(self, _sender: int, data: bytearray) -> None:
        """Handle notification responses."""
        _LOGGER.debug("%s: Notification received: %s", self.name, data.hex())

        self._notification_buffer += data
        msg = re.search(STATE_NOTIFICATION_REGEX, self._notification_buffer)
        if msg:
            self._notification_buffer = self._notification_buffer[msg.end() :]  # noqa: E203
            state_data = bytearray(msg.group())

            if ArtsaunaState.validate_ble_state_data(state_data):
                _LOGGER.debug("State notification found: %s", state_data)
                new_state = self._state.new_from_ble_state_data(state_data)
                self._state = new_state
                _LOGGER.debug("Setting new state: %s", new_state)

                self._fire_callbacks()
            else:
                _LOGGER.info("Incorrect state notification found: %s", data)
            msg = None

        msg = re.search(FM_NOTIFICATION_REGEX, self._notification_buffer)
        if msg:
            self._notification_buffer = self._notification_buffer[msg.end() :]  # noqa: E203
            fm_data = bytearray(msg.group())
            _LOGGER.debug("FM notification found: %s", fm_data)

            new_state = self._state.new_from_ble_fm_data(fm_data)
            self._state = new_state
            _LOGGER.debug("Setting new state: %s", new_state)
            self._fire_callbacks()

    async def _ensure_connected(self) -> None:
        """Ensure connection to device is established."""
        if self._connect_lock.locked():
            _LOGGER.debug(
                "%s: Connection already in progress, waiting for it to complete",
                self.name,
            )
        if self._client and self._client.is_connected:
            return
        async with self._connect_lock:
            # Check again while holding the lock
            if self._client and self._client.is_connected:
                return
            _LOGGER.debug("%s: Connecting", self.name)
            client = await establish_connection(
                BleakClientWithServiceCache,
                self._ble_device,
                self.name,
                self._disconnected,
                use_services_cache=True,
                ble_device_callback=lambda: self._ble_device,
            )
            _LOGGER.debug("%s: Connected", self.name)

            self._client = client

    async def _reconnect(self) -> None:
        """Attempt a reconnect"""
        _LOGGER.debug("ensuring connection")
        try:
            await self._ensure_connected()
            _LOGGER.debug("ensured connection - initialising")
            await self.initialise()
        except BleakNotFoundError:
            _LOGGER.debug("failed to ensure connection - backing off")
            await asyncio.sleep(BLEAK_BACKOFF_TIME)
            _LOGGER.debug("reconnecting again")
            asyncio.create_task(self._reconnect())

    # disconnect
    def _disconnected(self, client: BleakClientWithServiceCache) -> None:
        """Disconnected callback."""
        self._fire_disconnected_callbacks()
        if self._expected_disconnect:
            _LOGGER.debug("%s: Disconnected from device", self.name)
            return
        _LOGGER.warning(
            "%s: Device unexpectedly disconnected",
            self.name,
        )
        asyncio.create_task(self._reconnect())

    def _disconnect(self) -> None:
        """Disconnect from device."""
        asyncio.create_task(self._execute_timed_disconnect())

    async def stop(self) -> None:
        """Stop the Artsauna integration."""
        _LOGGER.debug("%s: Stop", self.name)
        await self._execute_disconnect()

    async def _execute_timed_disconnect(self) -> None:
        """Execute timed disconnection."""
        _LOGGER.debug(
            "%s: Disconnecting",
            self.name,
        )
        await self._execute_disconnect()

    async def _execute_disconnect(self) -> None:
        """Execute disconnection."""
        async with self._connect_lock:
            client = self._client
            self._expected_disconnect = True
            self._client = None
            if client and client.is_connected:
                await client.stop_notify(CHARACTERISTIC_NOTIFY)
                await client.disconnect()

    # commands
    async def _send_command(
        self, commands: list[bytes] | bytes, retry: int | None = None
    ) -> None:
        """Send command to device and read response."""
        await self._ensure_connected()
        if not isinstance(commands, list):
            commands = [commands]
        await self._send_command_while_connected(commands, retry)

    async def _send_command_while_connected(
        self, commands: list[bytes], retry: int | None = None
    ) -> None:
        """Send command to device and read response."""
        _LOGGER.debug(
            "%s: Sending commands %s",
            self.name,
            [command.hex() for command in commands],
        )
        if self._operation_lock.locked():
            _LOGGER.debug(
                "%s: Operation already in progress, waiting for it to complete",
                self.name,
            )
        async with self._operation_lock:
            try:
                await self._send_command_locked(commands)
                return
            except BleakNotFoundError:
                _LOGGER.exception(
                    "%s: device not found, no longer in range",
                    self.name,
                )
                raise
            except BLEAK_RETRY_EXCEPTIONS:
                _LOGGER.debug("%s: communication failed", self.name, exc_info=True)
                raise

    @retry_bluetooth_connection_error(DEFAULT_ATTEMPTS)
    async def _send_command_locked(self, commands: list[bytes]) -> None:
        """Send command to device and read response."""
        try:
            await self._execute_command_locked(commands)
        except BleakDBusError as ex:
            # Disconnect so we can reset state and try again
            await asyncio.sleep(BLEAK_BACKOFF_TIME)
            _LOGGER.debug(
                "%s: Backing off %ss; Disconnecting due to error: %s",
                self.name,
                BLEAK_BACKOFF_TIME,
                ex,
            )
            await self._execute_disconnect()
            raise
        except BleakError as ex:
            # Disconnect so we can reset state and try again
            _LOGGER.debug("%s: Disconnecting due to error: %s", self.name, ex)
            await self._execute_disconnect()
            raise

    async def _execute_command_locked(self, commands: list[bytes]) -> None:
        """Execute command and read response."""
        if self._client is not None:
            for command in commands:
                await self._client.write_gatt_char(CHARACTERISTIC_WRITE, data=command)

    # handle callbacks
    def register_callback(
        self, callback: Callable[[ArtsaunaState], None]
    ) -> Callable[[], None]:
        """Register a callback to be called when the state changes."""

        def unregister_callback() -> None:
            self._callbacks.remove(callback)

        self._callbacks.append(callback)
        return unregister_callback

    def _fire_callbacks(self) -> None:
        """Fire the callbacks."""
        for callback in self._callbacks:
            callback(self._state)

    def register_disconnected_callback(
        self, callback: Callable[[], None]
    ) -> Callable[[], None]:
        """Register a callback to be called when the state changes."""

        def unregister_callback() -> None:
            self._disconnected_callbacks.remove(callback)

        self._disconnected_callbacks.append(callback)
        return unregister_callback

    def _fire_disconnected_callbacks(self) -> None:
        """Fire the callbacks."""
        for callback in self._disconnected_callbacks:
            callback()
