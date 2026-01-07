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

from .artsauna_ble import ArtsaunaBLEAdapter
from .const import DOMAIN
from .coordinator import ArtsaunaBLECoordinator
from .models import ArtsaunaBLEData

_LOGGER = logging.getLogger(__name__)


TARGET_TEMP_DESCRIPTION = SensorEntityDescription(
    key="target_temp",
    name="Target Temperature",
    translation_key="target_temp",
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
)
CURRENT_TEMP_DESCRIPTION = SensorEntityDescription(
    key="current_temp",
    name="Current Temperature",
    translation_key="current_temp",
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
)
REMAINING_TIME_DESCRIPTION = SensorEntityDescription(
    key="remaining_time",
    name="Remaining Time",
    translation_key="remaining_time",
    device_class=SensorDeviceClass.DURATION,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfTime.MINUTES,
)
FM_FREQUENCY_DESCRIPTION = SensorEntityDescription(
    key="fm_frequency",
    name="FM Frequency",
    translation_key="fm_frequency",
    device_class=SensorDeviceClass.FREQUENCY,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfFrequency.MEGAHERTZ,
)

BUTTON_ENTITY_DESCRIPTIONS = [
    TARGET_TEMP_DESCRIPTION,
    CURRENT_TEMP_DESCRIPTION,
    REMAINING_TIME_DESCRIPTION,
    FM_FREQUENCY_DESCRIPTION,
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
        self._attr_unique_id = f"{device.name}_{self._key}_button"
        self._attr_device_info = DeviceInfo(
            name=name,
            connections={(device_registry.CONNECTION_BLUETOOTH, device.address)},
            manufacturer="HiMaterial",
            model="ArtsaunaBLE",
        )

    @property
    def available(self) -> bool:
        """Unavailable if coordinator isn't connected."""
        return self._coordinator.connected and super().available

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        match self._key:
            case "remaining_time":
                self._attr_native_value = self._device._state.remaining_time
            case "target_temp":
                self._attr_native_value = self._device._state.target_temp
            case "current_temp":
                self._attr_native_value = self._device._state.current_temp
            case "fm_frequency":
                self._attr_native_value = self._device._state.fm_frequency
            case _:
                _LOGGER.error("Wrong KEY for sensor: %s", self._key)
        self.async_write_ha_state()
