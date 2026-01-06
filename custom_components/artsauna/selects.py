"""Artsauna BLE integration sensor platform."""

import logging

from artsauna_ble.const import EXTERNAL_RGB_COLOR_MAP
from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ArtsaunaBLE, ArtsaunaBLECoordinator
from .const import DOMAIN
from .models import ArtsaunaBLEData

_LOGGER = logging.getLogger(__name__)

RGB_SELECT_DESCRIPTION = SelectEntityDescription(
    key="rgb",
    translation_key="rgb",
    options=list(EXTERNAL_RGB_COLOR_MAP.keys()),
    entity_category=EntityCategory.CONFIG,
)

SELECT_ENTITY_DESCRIPTIONS = [RGB_SELECT_DESCRIPTION]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the platform for ArtsaunaBLE."""
    data: ArtsaunaBLEData = hass.data[DOMAIN][entry.entry_id]

    entities = [
        ArtsaunaBLESelect(data.coordinator, data.device, entry.title, description)
        for description in SELECT_ENTITY_DESCRIPTIONS
    ]

    async_add_entities(entities)


class ArtsaunaBLESelect(CoordinatorEntity[ArtsaunaBLECoordinator], SelectEntity):
    """Generic sensor for ArtsaunaBLE."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG
    _attr_entity_registry_enabled_default = True
    _attr_entity_registry_visible_default = True

    def __init__(
        self,
        coordinator: ArtsaunaBLECoordinator,
        device: ArtsaunaBLE,
        name: str,
        description: SelectEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self.entity_description = description
        self._key = description.key
        self._device = device
        self._attr_unique_id = f"{device.name}_{self._key}_select"
        self._attr_device_info = DeviceInfo(
            name=name,
            connections={(device_registry.CONNECTION_BLUETOOTH, device.address)},
            manufacturer="HiLink",
            model="Artsauna",
            sw_version=getattr(self._device, "fw_ver"),
        )
        self._attr_current_option = EXTERNAL_RGB_COLOR_MAP.inverse[0]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        match self._key:
            case "rgb":
                self._attr_current_option = EXTERNAL_RGB_COLOR_MAP.inverse[
                    self._device.rgb_mode
                ]
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Unavailable if coordinator isn't connected."""
        return self._coordinator.connected and super().available

    async def async_select_option(self, option: str) -> None:
        await self._device.send_set_rgb(EXTERNAL_RGB_COLOR_MAP[option])
