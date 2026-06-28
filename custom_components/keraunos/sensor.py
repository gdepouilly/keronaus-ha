"""Sensor platform for the Keraunos storm-risk integration."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import KeraunosConfigEntry
from .const import DOMAIN, SENSORS
from .coordinator import KeraunosCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: KeraunosConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Keraunos sensors for a commune."""
    coordinator = entry.runtime_data
    async_add_entities(
        KeraunosSensor(coordinator, entry.unique_id, key)
        for key in SENSORS
    )


class KeraunosSensor(CoordinatorEntity[KeraunosCoordinator], SensorEntity):
    """A single storm-risk value for the configured commune."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: KeraunosCoordinator, insee: str, key: str
    ) -> None:
        """Initialise the sensor from a SENSORS descriptor."""
        super().__init__(coordinator)
        self._key = key
        name, icon = SENSORS[key]
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{insee}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, insee)},
            name=coordinator.data.get("town", insee),
            manufacturer="Keraunos",
            model="Risque orageux par commune",
            configuration_url=f"https://www.keraunos.org/site/risque/{insee}",
        )

    @property
    def native_value(self) -> str | None:
        """Return the current risk text for this sensor."""
        return self.coordinator.data.get(self._key)
