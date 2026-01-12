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
from homeassistant.const import EntityCategory, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .artsauna_ble import ArtsaunaBLEAdapter
from .const import DOMAIN
from .coordinator import ArtsaunaBLECoordinator
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

BUTTON_ENTITY_DESCRIPTIONS = [
    TEMP_UP_DESCRIPTION,
    TEMP_DOWN_DESCRIPTION,
    TIME_UP_DESCRIPTION,
    TIME_DOWN_DESCRIPTION,
    SEARCH_FM_DESCRIPTION,
    CYCLE_RGB_DESCRIPTION,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the platform for ArtsaunaBLE."""
    data: ArtsaunaBLEData = hass.data[DOMAIN][entry.entry_id]

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
        self._attr_unique_id = f"{device.name}_{self._key}_button"
        self._attr_name = f"{device.name}_button_{self._key}"
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
