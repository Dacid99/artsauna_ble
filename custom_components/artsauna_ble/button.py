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

"""Artsauna-BLE integration button platform."""

import logging

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_CLASS, EntityCategory, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .artsauna_ble import ArtsaunaBLEAdapter
from .const import SaunaDeviceType, DOMAIN
from .coordinator import ArtsaunaBLECoordinator
from .kdy_ble import KdyBLEAdapter
from .models import ArtsaunaBLEData

_LOGGER = logging.getLogger(__name__)


TEMP_UP_DESCRIPTION = ButtonEntityDescription(
    key="temp_up",
    icon="mdi:thermometer-plus",
    translation_key="temp_up",
    unit_of_measurement=UnitOfTemperature.CELSIUS,
)
TEMP_DOWN_DESCRIPTION = ButtonEntityDescription(
    key="temp_down",
    icon="mdi:thermometer-minus",
    translation_key="temp_down",
    unit_of_measurement=UnitOfTemperature.CELSIUS,
)
TIME_UP_DESCRIPTION = ButtonEntityDescription(
    key="time_up",
    icon="mdi:timer-plus-outline",
    translation_key="time_up",
    unit_of_measurement=UnitOfTime.MINUTES,
)
TIME_DOWN_DESCRIPTION = ButtonEntityDescription(
    key="time_down",
    icon="mdi:timer-minus-outline",
    translation_key="time_down",
    unit_of_measurement=UnitOfTime.MINUTES,
)
SEARCH_FM_DESCRIPTION = ButtonEntityDescription(
    key="search_fm",
    icon="mdi:radio",
    translation_key="search_fm",
)
CYCLE_RGB_DESCRIPTION = ButtonEntityDescription(
    key="cycle_rgb",
    translation_key="cycle_rgb",
    icon="mdi:palette",
)
EXTERNAL_LIGHT_DESCRIPTION = ButtonEntityDescription(
    key="external_light",
    translation_key="external_light",
    icon="mdi:lightbulb-outline",
)
INTERNAL_LIGHT_DESCRIPTION = ButtonEntityDescription(
    key="internal_light",
    translation_key="internal_light",
    icon="mdi:lightbulb-outline",
)
TOGGLE_AUDIO_SOURCE_DESCRIPTION = ButtonEntityDescription(
    key="toggle_audio_source",
    translation_key="toggle_audio_source",
    icon="mdi:bluetooth-audio",
)

BUTTON_ENTITY_DESCRIPTIONS = [
    TEMP_UP_DESCRIPTION,
    TEMP_DOWN_DESCRIPTION,
    TIME_UP_DESCRIPTION,
    TIME_DOWN_DESCRIPTION,
    SEARCH_FM_DESCRIPTION,
    CYCLE_RGB_DESCRIPTION,
]

KDY_BUTTON_ENTITY_DESCRIPTIONS = [
    TEMP_UP_DESCRIPTION,
    TEMP_DOWN_DESCRIPTION,
    TIME_UP_DESCRIPTION,
    TIME_DOWN_DESCRIPTION,
    EXTERNAL_LIGHT_DESCRIPTION,
    INTERNAL_LIGHT_DESCRIPTION,
    CYCLE_RGB_DESCRIPTION,
    TOGGLE_AUDIO_SOURCE_DESCRIPTION,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the platform for ArtsaunaBLE."""
    data: ArtsaunaBLEData = hass.data[DOMAIN][entry.entry_id]

    if entry.data.get(CONF_DEVICE_CLASS) == SaunaDeviceType.KDY:
        entities = [
            KdyBLEButton(data.coordinator, data.device, entry.title, description)
            for description in KDY_BUTTON_ENTITY_DESCRIPTIONS
        ]
    else:
        entities = [
            ArtsaunaBLEButton(data.coordinator, data.device, entry.title, description)
            for description in BUTTON_ENTITY_DESCRIPTIONS
        ]

    async_add_entities(entities)


class ArtsaunaBLEButton(CoordinatorEntity[ArtsaunaBLECoordinator], ButtonEntity):
    """Generic base button for ArtsaunaBLE."""

    _attr_has_entity_name = True
    _attr_device_class = ButtonDeviceClass.UPDATE
    _attr_entity_category = EntityCategory.CONFIG
    _attr_entity_registry_enabled_default = True
    _attr_entity_registry_visible_default = True

    def __init__(
        self,
        coordinator: ArtsaunaBLECoordinator,
        device: ArtsaunaBLEAdapter,
        name: str,
        description: ButtonEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self.entity_description = description
        self._key = description.key
        self._device = device
        self._attr_unique_id = f"{device.address}_{self._key}"
        self._attr_device_info = DeviceInfo(
            name=name,
            connections={(device_registry.CONNECTION_BLUETOOTH, device.address)},
            manufacturer="HiMaterial",
            model="ArtsaunaBLE",
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        match self._key:
            case "search_fm":
                return await self._device.send_toggle_fm()
            case "temp_up":
                return await self._device.send_temp_up()
            case "temp_down":
                return await self._device.send_temp_down()
            case "time_up":
                return await self._device.send_time_up()
            case "time_down":
                return await self._device.send_time_down()
            case "cycle_rgb":
                return await self._device.send_cycle_rgb()
            case _:
                _LOGGER.error("Wrong KEY for button: %s", self._key)

    @property
    def available(self) -> bool:
        match self._key:
            case "temp_up" | "temp_down" | "time_up" | "time_down":
                return (
                    super().available
                    and self._device.is_power_on
                    and self._device.is_heating_on
                )
        return super().available and self._device.is_power_on


class KdyBLEButton(CoordinatorEntity[ArtsaunaBLECoordinator], ButtonEntity):
    """Button for KDY Sauna BLE devices."""

    _attr_has_entity_name = True
    _attr_device_class = ButtonDeviceClass.UPDATE
    _attr_entity_category = EntityCategory.CONFIG
    _attr_entity_registry_enabled_default = True
    _attr_entity_registry_visible_default = True

    def __init__(
        self,
        coordinator: ArtsaunaBLECoordinator,
        device: KdyBLEAdapter,
        name: str,
        description: ButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self.entity_description = description
        self._key = description.key
        self._device = device
        self._attr_unique_id = f"{device.address}_{self._key}"
        self._attr_device_info = DeviceInfo(
            name=name,
            connections={(device_registry.CONNECTION_BLUETOOTH, device.address)},
            manufacturer="KDY",
            model="KDYSauna",
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        match self._key:
            case "temp_up":
                return await self._device.send_temp_up()
            case "temp_down":
                return await self._device.send_temp_down()
            case "time_up":
                return await self._device.send_timer_up()
            case "time_down":
                return await self._device.send_timer_down()
            case "external_light":
                return await self._device.send_toggle_external_light()
            case "internal_light":
                return await self._device.send_toggle_internal_light()
            case "cycle_rgb":
                return await self._device.send_cycle_rgb()
            case "toggle_audio_source":
                return await self._device.send_toggle_audio_source()
            case _:
                _LOGGER.error("Wrong KEY for KDY button: %s", self._key)

    @property
    def available(self) -> bool:
        match self._key:
            case "temp_up" | "temp_down" | "time_up" | "time_down":
                return super().available and self._device.is_power_on
        return super().available
