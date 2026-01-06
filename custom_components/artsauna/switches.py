"""Artsauna BLE integration sensor platform."""

import logging
from functools import cached_property
from typing import Any

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
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


POWER_DESCRIPTION = SwitchEntityDescription(
    key="power",
    translation_key="power",
)

HEATING_DESCRIPTION = SwitchEntityDescription(
    key="heating",
    translation_key="heating",
)

EXTERNAL_LIGHT_DESCRIPTION = SwitchEntityDescription(
    key="external_light",
    translation_key="external_light",
)

INTERNAL_LIGHT_DESCRIPTION = SwitchEntityDescription(
    key="internal_light",
    translation_key="internal_light",
)

AUX_DESCRIPTION = SwitchEntityDescription(
    key="aux",
    translation_key="aux",
)

FM_DESCRIPTION = SwitchEntityDescription(
    key="fm",
    translation_key="fm",
)

USB_DESCRIPTION = SwitchEntityDescription(
    key="usb",
    translation_key="usb",
)

BT_DESCRIPTION = SwitchEntityDescription(
    key="bt",
    translation_key="bluetooth",
)
UNIT_DESCRIPTION = SwitchEntityDescription(
    key="unit",
    translation_key="unit",
)

SWITCH_ENTITY_DESCRIPTIONS = [
    POWER_DESCRIPTION,
    HEATING_DESCRIPTION,
    USB_DESCRIPTION,
    AUX_DESCRIPTION,
    BT_DESCRIPTION,
    FM_DESCRIPTION,
    EXTERNAL_LIGHT_DESCRIPTION,
    INTERNAL_LIGHT_DESCRIPTION,
    UNIT_DESCRIPTION,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the platform for ArtsaunaBLE."""
    data: ArtsaunaBLEData = hass.data[DOMAIN][entry.entry_id]

    entities = [
        ArtsaunaBLESwitch(data.coordinator, data.device, entry.title, description)
        for description in SWITCH_ENTITY_DESCRIPTIONS
    ]

    async_add_entities(entities)


class ArtsaunaBLESwitch(CoordinatorEntity[ArtsaunaBLECoordinator], SwitchEntity):
    """Generic sensor for ArtsaunaBLE."""

    _attr_has_entity_name = True
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_entity_category = EntityCategory.CONFIG
    _attr_entity_registry_enabled_default = True
    _attr_entity_registry_visible_default = True

    def __init__(
        self,
        coordinator: ArtsaunaBLECoordinator,
        device: ArtsaunaBLE,
        name: str,
        description: SwitchEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self.entity_description = description
        self._key = description.key
        self._device = device
        self._attr_unique_id = f"{device.name}_{self._key}_switch"
        self._attr_device_info = DeviceInfo(
            name=name,
            connections={(device_registry.CONNECTION_BLUETOOTH, device.address)},
            manufacturer="HiLink",
            model="Artsauna",
            sw_version=getattr(self._device, "fw_ver"),
        )
        self._attr_native_value = getattr(self._device, "target_mode")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = getattr(self._device, "target_mode")
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Unavailable if coordinator isn't connected."""
        return self._coordinator.connected and super().available

    @cached_property
    def is_on(self) -> bool:
        match self._key:
            case "power":
                return self._device.power_on
            case "heating":
                return self._device.heating_on
            case "external_light":
                return self._device.external_lighting_on
            case "internal_light":
                return self._device.internal_lighting_on
            case "aux":
                return self._device.is_aux_on
            case "usb":
                return self._device.is_usb_on
            case "bt":
                return self._device.is_bt_on
            case "fm":
                return self._device.is_fm_on
            case "unit":
                return self._device.is_unit_celsius
            case _:
                _LOGGER.error("Wrong KEY for switch: %s", self._key)
                return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        match self._key:
            case "power":
                await self._device.send_toggle_power()
            case "heating":
                await self._device.send_toggle_heating()
            case "external_light":
                await self._device.send_toggle_external_light()
            case "internal_light":
                await self._device.send_toggle_internal_light()
            case "aux":
                await self._device.send_toggle_aux()
            case "usb":
                await self._device.send_toggle_usb()
            case "bt":
                await self._device.send_toggle_bt()
            case "fm":
                await self._device.send_toggle_fm()
            case "unit":
                await self._device.send_toggle_unit()
            case _:
                _LOGGER.error("Wrong KEY for switch: %s", self._key)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.async_turn_on()
