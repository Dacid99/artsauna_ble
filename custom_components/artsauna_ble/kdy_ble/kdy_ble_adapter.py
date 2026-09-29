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

"""Single-connection KDY Sauna BLE adapter.

All status notifications and commands use this one Bleak client. Commands
are sent as write-without-response on FFF1, one byte at a time, per
PROTOCOL.md. Power, timer, target temperature, outside/inside light, RGB, FM, and unit
toggle are confirmed against real hardware; volume, BT, and USB are
decompiled-app values, not yet confirmed — see PROTOCOL.md. In particular,
power has no explicit OFF and must be gated on the current status.
"""

from __future__ import annotations

import asyncio
import logging
import sys
from collections.abc import Callable
from functools import cached_property

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
from homeassistant.helpers.device_registry import format_mac

from .const import (
    CHARACTERISTIC_FFF1,
    CHARACTERISTIC_FFF2,
    CMD_BYTE_BT,
    CMD_BYTE_FM,
    CMD_BYTE_INSIDE_LIGHT,
    CMD_BYTE_OUTSIDE_LIGHT,
    CMD_BYTE_POWER,
    CMD_BYTE_RGB,
    CMD_BYTE_TARGET_TEMP,
    CMD_BYTE_TIMER,
    CMD_BYTE_UNIT,
    CMD_BYTE_USB,
    CMD_BYTE_VOLUME,
    CMD_VALUE_STEP_DOWN,
    CMD_VALUE_STEP_UP,
    CMD_VALUE_TOGGLE,
    short_uuid,
)
from .models import InvalidStatusPacket, KdyState, build_command_packet

_LOGGER = logging.getLogger(__name__)
BLEAK_BACKOFF_TIME = 0.25
DEFAULT_ATTEMPTS = sys.maxsize


class KdyBLEAdapter:
    """KDY Sauna BLE adapter with a single shared connection."""

    def __init__(self, ble_device: BLEDevice) -> None:
        self._ble_device = ble_device
        self._advertisement_data: AdvertisementData | None = None
        self._state = KdyState()
        self._client: BleakClientWithServiceCache | None = None
        self._connect_lock = asyncio.Lock()
        self._operation_lock = asyncio.Lock()
        self._callbacks: list[Callable[[KdyState], None]] = []
        self._disconnected_callbacks: list[Callable[[], None]] = []
        self._expected_disconnect = False

    @cached_property
    def address(self) -> str:
        """Return the address."""
        return format_mac(self._ble_device.address)

    @cached_property
    def name(self) -> str:
        """Get the name of the device."""
        return self._ble_device.name or self.address

    @property
    def state(self) -> KdyState:
        return self._state

    @property
    def is_power_on(self) -> bool:
        return self._state.power

    @property
    def target_temp(self) -> int:
        return self._state.target_temp

    @property
    def current_temp(self) -> int:
        return self._state.current_temp

    @property
    def remaining_time(self) -> int:
        return self._state.remaining_minutes

    @property
    def volume(self) -> int:
        return self._state.volume

    @property
    def is_fm_on(self) -> bool:
        return self._state.fm_on

    @property
    def is_bt_on(self) -> bool:
        return self._state.bt_on

    @property
    def is_usb_on(self) -> bool:
        return self._state.usb_on

    @property
    def is_unit_celsius(self) -> bool:
        return not self._state.unit_fahrenheit

    async def initialise(self) -> None:
        """Connect and subscribe to notifications on the shared client."""
        await self._ensure_connected()

        if self._client is None:
            _LOGGER.debug("%s: Client is unexpectedly None", self.name)
            return

        _LOGGER.debug("%s: Subscribe to FFF2 status notifications", self.name)
        await self._client.start_notify(CHARACTERISTIC_FFF2, self._notification_handler)
        # FFF1 also has notify — log RAW only until meaning is verified
        try:
            await self._client.start_notify(
                CHARACTERISTIC_FFF1, self._notification_handler
            )
            _LOGGER.debug("%s: Also subscribed to FFF1 for RAW logging", self.name)
        except BleakError:
            _LOGGER.debug(
                "%s: FFF1 notify subscribe failed (optional)", self.name, exc_info=True
            )

    def set_ble_device_and_advertisement_data(
        self, ble_device: BLEDevice, advertisement_data: AdvertisementData
    ) -> None:
        """Set the ble device."""
        self._ble_device = ble_device
        self._advertisement_data = advertisement_data

    def _notification_handler(self, characteristic: object, data: bytearray) -> None:
        """Handle notification responses on the single connection."""
        char_uuid = getattr(characteristic, "uuid", None)
        label = short_uuid(str(char_uuid)) if char_uuid else "UNKNOWN"
        raw_hex = bytes(data).hex()
        _LOGGER.debug("%s: RAW notification %s: %s", self.name, label, raw_hex)

        # Status frames have been observed on both FFF1 and FFF2 on real
        # hardware; the AA...CC framing check below is what validates a
        # payload as a genuine status packet, not the source characteristic.
        try:
            new_state = KdyState.from_ble_status(data)
        except InvalidStatusPacket:
            _LOGGER.debug(
                "%s: Non-status or invalid %s payload (kept as RAW only): %s",
                self.name,
                label,
                raw_hex,
            )
            return

        self._state = new_state
        _LOGGER.debug(
            "%s: Decoded status: %s | RAW: %s",
            self.name,
            new_state.format_known_fields(),
            raw_hex,
        )
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
        """Attempt a reconnect on the same adapter instance."""
        _LOGGER.debug("%s: ensuring connection", self.name)
        try:
            await self._ensure_connected()
            _LOGGER.debug("%s: ensured connection - initialising", self.name)
            await self.initialise()
        except BleakNotFoundError:
            _LOGGER.debug("%s: failed to ensure connection - backing off", self.name)
            await asyncio.sleep(BLEAK_BACKOFF_TIME)
            asyncio.create_task(self._reconnect())

    def _disconnected(self, client: BleakClientWithServiceCache) -> None:
        """Disconnected callback."""
        self._fire_disconnected_callbacks()
        if self._expected_disconnect:
            _LOGGER.debug("%s: Disconnected from device", self.name)
            return
        _LOGGER.warning("%s: Device unexpectedly disconnected", self.name)
        asyncio.create_task(self._reconnect())

    async def stop(self) -> None:
        """Stop the KDY BLE connection."""
        _LOGGER.debug("%s: Stop", self.name)
        await self._execute_disconnect()

    async def _execute_disconnect(self) -> None:
        """Execute disconnection."""
        async with self._connect_lock:
            client = self._client
            self._expected_disconnect = True
            self._client = None
            if client and client.is_connected:
                for char in (CHARACTERISTIC_FFF2, CHARACTERISTIC_FFF1):
                    try:
                        await client.stop_notify(char)
                    except BleakError:
                        _LOGGER.debug(
                            "%s: stop_notify %s failed",
                            self.name,
                            short_uuid(char),
                            exc_info=True,
                        )
                await client.disconnect()

    # commands
    async def send_toggle_power(self) -> None:
        """Toggle power. No explicit OFF — see PROTOCOL.md safety notes."""
        await self._send_command(CMD_BYTE_POWER, CMD_VALUE_TOGGLE)

    async def send_timer_up(self) -> None:
        await self._send_command(CMD_BYTE_TIMER, CMD_VALUE_STEP_UP)

    async def send_timer_down(self) -> None:
        await self._send_command(CMD_BYTE_TIMER, CMD_VALUE_STEP_DOWN)

    async def send_temp_up(self) -> None:
        await self._send_command(CMD_BYTE_TARGET_TEMP, CMD_VALUE_STEP_UP)

    async def send_temp_down(self) -> None:
        await self._send_command(CMD_BYTE_TARGET_TEMP, CMD_VALUE_STEP_DOWN)

    async def send_toggle_outside_light(self) -> None:
        await self._send_command(CMD_BYTE_OUTSIDE_LIGHT, CMD_VALUE_TOGGLE)

    async def send_toggle_inside_light(self) -> None:
        await self._send_command(CMD_BYTE_INSIDE_LIGHT, CMD_VALUE_TOGGLE)

    async def send_cycle_rgb(self) -> None:
        await self._send_command(CMD_BYTE_RGB, CMD_VALUE_TOGGLE)

    async def send_set_volume(self, volume: int) -> None:
        """Set volume 1-20 (absolute — the one command that isn't a step)."""
        await self._send_command(CMD_BYTE_VOLUME, volume)

    async def send_toggle_fm(self) -> None:
        await self._send_command(CMD_BYTE_FM, CMD_VALUE_TOGGLE)

    async def send_toggle_audio_source(self) -> None:
        """Swap between BT and USB audio source.

        The app sends byte 16 (USB) if BT is currently on, else byte 15
        (BT) — there is no independent on/off, only a swap.
        """
        byte_index = CMD_BYTE_USB if self._state.bt_on else CMD_BYTE_BT
        await self._send_command(byte_index, CMD_VALUE_TOGGLE)

    async def send_toggle_unit(self) -> None:
        await self._send_command(CMD_BYTE_UNIT, CMD_VALUE_TOGGLE)

    async def _send_command(self, byte_index: int, value: int) -> None:
        """Send a single-byte command to the device."""
        await self._ensure_connected()
        await self._send_command_while_connected(byte_index, value)

    async def _send_command_while_connected(self, byte_index: int, value: int) -> None:
        """Send command to device while holding the operation lock."""
        packet = build_command_packet(byte_index, value)
        _LOGGER.debug("%s: Sending command %s", self.name, packet.hex())
        if self._operation_lock.locked():
            _LOGGER.debug(
                "%s: Operation already in progress, waiting for it to complete",
                self.name,
            )
        async with self._operation_lock:
            try:
                await self._send_command_locked(packet)
            except BleakNotFoundError:
                _LOGGER.exception("%s: device not found, no longer in range", self.name)
                raise
            except BLEAK_RETRY_EXCEPTIONS:
                _LOGGER.debug("%s: communication failed", self.name, exc_info=True)
                raise

    @retry_bluetooth_connection_error(DEFAULT_ATTEMPTS)
    async def _send_command_locked(self, packet: bytes) -> None:
        """Write a command packet, disconnecting on error to allow retry."""
        try:
            if self._client is not None:
                await self._client.write_gatt_char(
                    CHARACTERISTIC_FFF1, data=packet, response=False
                )
        except BleakDBusError as ex:
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
            _LOGGER.debug("%s: Disconnecting due to error: %s", self.name, ex)
            await self._execute_disconnect()
            raise

    def register_callback(
        self, callback: Callable[[KdyState], None]
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
        """Register a callback to be called when disconnected."""

        def unregister_callback() -> None:
            self._disconnected_callbacks.remove(callback)

        self._disconnected_callbacks.append(callback)
        return unregister_callback

    def _fire_disconnected_callbacks(self) -> None:
        """Fire the disconnected callbacks."""
        for callback in self._disconnected_callbacks:
            callback()
