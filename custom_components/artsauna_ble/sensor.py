"""LD2450 BLE integration sensor platform."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    EntityCategory,
    UnitOfFrequency,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from propcache.api import cached_property

from custom_components.artsauna_ble.artsauna_ble.const import INTERNAL_RGB_COLOR_MAP

from .artsauna_ble import ArtsaunaBLEAdapter
from .const import DOMAIN
from .coordinator import ArtsaunaBLECoordinator
from .models import ArtsaunaBLEData

_LOGGER = logging.getLogger(__name__)


TARGET_TEMP_DESCRIPTION = SensorEntityDescription(
    key="target_temp",
    translation_key="target_temp",
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
)
CURRENT_TEMP_DESCRIPTION = SensorEntityDescription(
    key="current_temp",
    translation_key="current_temp",
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
)
REMAINING_TIME_DESCRIPTION = SensorEntityDescription(
    key="remaining_time",
    translation_key="remaining_time",
    device_class=SensorDeviceClass.DURATION,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfTime.MINUTES,
)
FM_FREQUENCY_DESCRIPTION = SensorEntityDescription(
    key="fm_frequency",
    translation_key="fm_frequency",
    device_class=SensorDeviceClass.FREQUENCY,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfFrequency.MEGAHERTZ,
)
RGB_MODE_DESCRIPTION = SensorEntityDescription(
    key="rgb_mode",
    translation_key="rgb_mode",
    icon="mdi:palette",
)

BUTTON_ENTITY_DESCRIPTIONS = [
    TARGET_TEMP_DESCRIPTION,
    CURRENT_TEMP_DESCRIPTION,
    REMAINING_TIME_DESCRIPTION,
    FM_FREQUENCY_DESCRIPTION,
    RGB_MODE_DESCRIPTION,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the platform for ArtsaunaBLE."""
    data: ArtsaunaBLEData = hass.data[DOMAIN][entry.entry_id]

    entities = [
        ArtsaunaBLESensor(data.coordinator, data.device, entry.title, description)
        for description in BUTTON_ENTITY_DESCRIPTIONS
    ]

    async_add_entities(entities)


class ArtsaunaBLESensor(CoordinatorEntity[ArtsaunaBLECoordinator], SensorEntity):
    """Generic base button for ArtsaunaBLE."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = True
    _attr_entity_registry_visible_default = True

    def __init__(
        self,
        coordinator: ArtsaunaBLECoordinator,
        device: ArtsaunaBLEAdapter,
        name: str,
        description: SensorEntityDescription,
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

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        match self._key:
            case "remaining_time":
                self._attr_native_value = self._device.remaining_time
            case "target_temp":
                self._attr_native_value = self._device.target_temp
            case "current_temp":
                self._attr_native_value = self._device.current_temp
            case "fm_frequency":
                self._attr_native_value = self._device.fm_frequency
            case "rgb_mode":
                self._attr_native_value = self._device.rgb_mode
            case _:
                _LOGGER.error("Wrong KEY for sensor: %s", self._key)
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        return super().available and self._device.is_power_on

    @cached_property
    def native_value(self):
        if self._key == "rgb_mode":
            return INTERNAL_RGB_COLOR_MAP.inverse[self._attr_native_value]
        return super().native_value

    @cached_property
    def native_unit_of_measurement(self) -> str | None:
        if self._key in ["current_temp", "target_temp"]:
            return (
                UnitOfTemperature.CELSIUS
                if self._device.is_unit_celsius
                else UnitOfTemperature.FAHRENHEIT
            )
        return super().native_unit_of_measurement
