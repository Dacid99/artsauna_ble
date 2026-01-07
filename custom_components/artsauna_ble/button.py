"""LD2450 BLE integration sensor platform."""

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
    translation_key="temp_up",
    name="Temp +",
    unit_of_measurement=UnitOfTemperature.CELSIUS,
)
TEMP_DOWN_DESCRIPTION = ButtonEntityDescription(
    key="temp_down",
    name="Temp -",
    translation_key="temp_down",
    unit_of_measurement=UnitOfTemperature.CELSIUS,
)
TIME_UP_DESCRIPTION = ButtonEntityDescription(
    key="time_up",
    name="TIME +",
    translation_key="time_up",
    unit_of_measurement=UnitOfTime.MINUTES,
)
TIME_DOWN_DESCRIPTION = ButtonEntityDescription(
    key="time_down",
    name="TIME -",
    translation_key="time_down",
    unit_of_measurement=UnitOfTime.MINUTES,
)
SEARCH_FM_DESCRIPTION = ButtonEntityDescription(
    key="search_fm",
    name="Search Radiostations",
    translation_key="search_fm",
)

BUTTON_ENTITY_DESCRIPTIONS = [
    TEMP_UP_DESCRIPTION,
    TEMP_DOWN_DESCRIPTION,
    TIME_UP_DESCRIPTION,
    TIME_DOWN_DESCRIPTION,
    SEARCH_FM_DESCRIPTION,
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
            case _:
                _LOGGER.error("Wrong KEY for button: %s", self._key)
