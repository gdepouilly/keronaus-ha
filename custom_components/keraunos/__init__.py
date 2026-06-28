"""The Keraunos storm-risk integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_INSEE, DOMAIN
from .coordinator import KeraunosCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]

type KeraunosConfigEntry = ConfigEntry[KeraunosCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: KeraunosConfigEntry) -> bool:
    """Set up Keraunos from a config entry."""
    coordinator = KeraunosCoordinator(hass, entry, entry.data[CONF_INSEE])
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload when the options flow changes the commune.
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: KeraunosConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload_entry(hass: HomeAssistant, entry: KeraunosConfigEntry) -> None:
    """Reload the entry after an options update."""
    await hass.config_entries.async_reload(entry.entry_id)
