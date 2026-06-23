"""NISS Broadband sensors."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NissDataCoordinator
from .const import DOMAIN, SENSOR_ICONS, SENSOR_TYPES


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    coordinator: NissDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        NissSensor(coordinator, entry, sensor_type) for sensor_type in SENSOR_TYPES
    )


class NissSensor(CoordinatorEntity, SensorEntity):
    """A single NISS usage sensor backed by the shared coordinator."""

    _attr_native_unit_of_measurement = "GB"
    _attr_state_class = SensorStateClass.TOTAL
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NissDataCoordinator,
        entry: ConfigEntry,
        sensor_type: str,
    ) -> None:
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = f"NISS {sensor_type.capitalize()} Data"
        # Tie unique_id to the config entry so multiple accounts could coexist
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}_usage"
        self._attr_icon = SENSOR_ICONS.get(sensor_type, "mdi:network")

    @property
    def native_value(self) -> float | None:
        """Return the parsed GB value from the coordinator."""
        return self.coordinator.data.get(self._sensor_type)

    @property
    def available(self) -> bool:
        """Mark unavailable if the coordinator has no data for this sensor."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self._sensor_type in self.coordinator.data
        )
