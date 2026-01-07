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

from .artsauna_ble import ArtsaunaBLEAdapter
from .const import DOMAIN
from .coordinator import ArtsaunaBLECoordinator
from .models import ArtsaunaBLEData

_LOGGER = logging.getLogger(__name__)


POWER_DESCRIPTION = SwitchEntityDescription(
    key="power",
    name="Power",
    icon="mdi:power_settings_new",
    translation_key="power",
)

HEATING_DESCRIPTION = SwitchEntityDescription(
    key="heating",
    name="Heating",
    icon="mdi:heat",
    translation_key="heating",
)

EXTERNAL_LIGHT_DESCRIPTION = SwitchEntityDescription(
    key="external_light",
    name="External Light",
    translation_key="external_light",
)

INTERNAL_LIGHT_DESCRIPTION = SwitchEntityDescription(
    key="internal_light",
    name="Internal Light",
    translation_key="internal_light",
)

AUX_DESCRIPTION = SwitchEntityDescription(
    key="aux",
    name="AUX Mode",
    translation_key="aux",
)

FM_DESCRIPTION = SwitchEntityDescription(
    key="fm",
    name="Radio Mode",
    icon="mdi:radio",
    translation_key="fm",
)

USB_DESCRIPTION = SwitchEntityDescription(
    key="usb",
    name="USB Mode",
    translation_key="usb",
)

BT_DESCRIPTION = SwitchEntityDescription(
    key="bt",
    name="BT Mode",
    icon="mdi:bluetooth",
    translation_key="bluetooth",
)
UNIT_DESCRIPTION = SwitchEntityDescription(
    key="unit",
    name="Temperature Unit",
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
        device: ArtsaunaBLEAdapter,
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
            manufacturer="HiMaterial",
            model="Artsauna",
        )
        self._attr_is_on = False

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        match self._key:
            case "power":
                self._attr_is_on = self._device.is_power_on
            case "heating":
                self._attr_is_on = self._device.is_heating_on
            case "external_light":
                self._attr_is_on = self._device.is_external_light_on
            case "internal_light":
                self._attr_is_on = self._device.is_internal_light_on
            case "aux":
                self._attr_is_on = self._device.is_aux_on
            case "usb":
                self._attr_is_on = self._device.is_usb_on
            case "bt":
                self._attr_is_on = self._device.is_bt_on
            case "fm":
                self._attr_is_on = self._device.is_fm_on
            case "unit":
                self._attr_is_on = self._device.is_unit_celsius
            case _:
                _LOGGER.error("Wrong KEY for switch: %s", self._key)

        self.async_write_ha_state()

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
