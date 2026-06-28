"""The Keraunos storm-risk integration."""

from __future__ import annotations

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_point_in_time
import homeassistant.util.dt as dt_util

from .const import CONF_INSEE, DOMAIN, PARIS_TZ, REFRESH_TIMES
from .coordinator import KeraunosCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR]

type KeraunosConfigEntry = ConfigEntry[KeraunosCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: KeraunosConfigEntry) -> bool:
    """Set up Keraunos from a config entry."""
    coordinator = KeraunosCoordinator(hass, entry, entry.data[CONF_INSEE])
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Refresh once a day just after the morning publish window (Europe/Paris),
    # instead of polling — the upstream data only changes once between 08:00 and
    # 09:00 French time.
    _schedule_daily_refreshes(hass, entry, coordinator)

    # Reload when the options flow changes the commune.
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


def _next_paris_run(target: time) -> datetime:
    """Return the next datetime at ``target`` Europe/Paris time, as aware UTC-safe."""
    tz = ZoneInfo(PARIS_TZ)
    now = dt_util.utcnow().astimezone(tz)
    run = now.replace(
        hour=target.hour, minute=target.minute, second=0, microsecond=0
    )
    if run <= now:
        run += timedelta(days=1)
    return run


@callback
def _schedule_daily_refreshes(
    hass: HomeAssistant,
    entry: KeraunosConfigEntry,
    coordinator: KeraunosCoordinator,
) -> None:
    """Schedule a daily refresh at each configured Europe/Paris time."""

    def _schedule(target: time) -> None:
        @callback
        def _fire(_now: datetime) -> None:
            hass.async_create_task(coordinator.async_request_refresh())
            _schedule(target)  # re-arm for the next day

        entry.async_on_unload(
            async_track_point_in_time(hass, _fire, _next_paris_run(target))
        )

    for target in REFRESH_TIMES:
        _schedule(target)


async def async_unload_entry(hass: HomeAssistant, entry: KeraunosConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload_entry(hass: HomeAssistant, entry: KeraunosConfigEntry) -> None:
    """Reload the entry after an options update."""
    await hass.config_entries.async_reload(entry.entry_id)
