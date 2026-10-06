"""Sauna BLE integration sensor platform."""

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
from .const import (
    HASS_DOMAIN,
)
from .coordinator import ArtsaunaBLECoordinator
from .kdy_ble import KdyBLEAdapter
from .models import ArtsaunaBLEData

_LOGGER = logging.getLogger(__name__)


TARGET_TEMP_DESCRIPTION = SensorEntityDescription(
    key="target_temp",
    translation_key="target_temp",
    icon="mdi:thermometer",
    # device_class=SensorDeviceClass.TEMPERATURE, # don't set temperature to allow switching between F and C
    state_class=SensorStateClass.MEASUREMENT,
)
CURRENT_TEMP_DESCRIPTION = SensorEntityDescription(
    key="current_temp",
    translation_key="current_temp",
    icon="mdi:thermometer",
    # device_class=SensorDeviceClass.TEMPERATURE,
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
POWER_DESCRIPTION = SensorEntityDescription(
    key="power",
    translation_key="power",
    icon="mdi:power",
)

ARTSAUNA_SENSOR_DESCRIPTIONS = [
    TARGET_TEMP_DESCRIPTION,
    CURRENT_TEMP_DESCRIPTION,
    REMAINING_TIME_DESCRIPTION,
    FM_FREQUENCY_DESCRIPTION,
    RGB_MODE_DESCRIPTION,
]

KDY_SENSOR_DESCRIPTIONS = [
    POWER_DESCRIPTION,
    TARGET_TEMP_DESCRIPTION,
    CURRENT_TEMP_DESCRIPTION,
    REMAINING_TIME_DESCRIPTION,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    data: ArtsaunaBLEData = hass.data[HASS_DOMAIN][entry.entry_id]
    if data and data.device:
        if isinstance(data.device, KdyBLEAdapter):
            entities = [
                KdyBLESensor(data.coordinator, data.device, entry.title, description)
                for description in KDY_SENSOR_DESCRIPTIONS
            ]
        else:
            entities = [
                ArtsaunaBLESensor(data.coordinator, data.device, entry.title, description)
                for description in ARTSAUNA_SENSOR_DESCRIPTIONS
            ]
        async_add_entities(entities)


class ArtsaunaBLESensor(CoordinatorEntity[ArtsaunaBLECoordinator], SensorEntity):
    """Sensor for Artsauna BLE devices."""

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
                self._sensor_option_unit_of_measurement = (
                    UnitOfTemperature.CELSIUS
                    if self._device.is_unit_celsius
                    else UnitOfTemperature.FAHRENHEIT
                )
            case "current_temp":
                self._attr_native_value = self._device.current_temp
                self._sensor_option_unit_of_measurement = (
                    UnitOfTemperature.CELSIUS
                    if self._device.is_unit_celsius
                    else UnitOfTemperature.FAHRENHEIT
                )
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
            try:
                return INTERNAL_RGB_COLOR_MAP.inverse[self._attr_native_value]
            except KeyError:
                return None
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


class KdyBLESensor(CoordinatorEntity[ArtsaunaBLECoordinator], SensorEntity):
    """Sensor for KDY Sauna BLE devices."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = True
    _attr_entity_registry_visible_default = True

    def __init__(
        self,
        coordinator: ArtsaunaBLECoordinator,
        device: KdyBLEAdapter,
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
            manufacturer="KDY",
            model="KDYSauna",
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        match self._key:
            case "power":
                self._attr_native_value = "on" if self._device.is_power_on else "off"
            case "remaining_time":
                self._attr_native_value = self._device.remaining_time
            case "target_temp":
                self._attr_native_value = self._device.target_temp
                self._sensor_option_unit_of_measurement = (
                    UnitOfTemperature.CELSIUS
                    if self._device.is_unit_celsius
                    else UnitOfTemperature.FAHRENHEIT
                )
            case "current_temp":
                self._attr_native_value = self._device.current_temp
                self._sensor_option_unit_of_measurement = (
                    UnitOfTemperature.CELSIUS
                    if self._device.is_unit_celsius
                    else UnitOfTemperature.FAHRENHEIT
                )
            case _:
                _LOGGER.error("Wrong KEY for KDY sensor: %s", self._key)
                return
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        return super().available and self._coordinator.connected

    @cached_property
    def native_unit_of_measurement(self) -> str | None:
        if self._key in ["current_temp", "target_temp"]:
            return (
                UnitOfTemperature.CELSIUS
                if self._device.is_unit_celsius
                else UnitOfTemperature.FAHRENHEIT
            )
        return super().native_unit_of_measurement
