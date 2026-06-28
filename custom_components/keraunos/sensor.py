"""Sensor platform for the Keraunos storm-risk integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import KeraunosConfigEntry
from .const import DOMAIN, LEVEL_MAX, SENSORS
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
    """A single storm-risk category for the configured commune.

    The state is the human-readable French text; the gravity level (0..5),
    colour and range are exposed as attributes.
    """

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: KeraunosCoordinator, insee: str, key: str
    ) -> None:
        """Initialise the sensor from a SENSORS descriptor."""
        super().__init__(coordinator)
        self._key = key
        meta = SENSORS[key]
        self._kind = meta["kind"]
        self._attr_name = meta["name"]
        self._attr_icon = meta["icon"]
        self._attr_unique_id = f"{insee}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, insee)},
            name=coordinator.data.get("town", insee),
            manufacturer="Keraunos",
            model="Risque orageux par commune",
            configuration_url=f"https://www.keraunos.org/site/risque/{insee}",
        )

    @property
    def _entry(self) -> dict[str, Any]:
        """Return this sensor's parsed entry from the coordinator."""
        return self.coordinator.data.get(self._key) or {}

    @property
    def native_value(self) -> str | None:
        """Return the human-readable risk text."""
        return self._entry.get("description")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose the gravity level (0..5), colour and range as attributes."""
        entry = self._entry
        attrs: dict[str, Any] = {
            "level": entry.get("level"),
            "level_max": LEVEL_MAX,
            "color": entry.get("color"),
        }
        if self._kind == "severity":
            attrs["level_label"] = entry.get("label")
        else:
            attrs["probability_range"] = entry.get("range")
        return attrs
