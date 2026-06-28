"""Data update coordinator for the Keraunos storm-risk integration."""

from __future__ import annotations

import logging
import re

import aiohttp
from bs4 import BeautifulSoup

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import BADGE_COUNT, BASE_URL, DEFAULT_SCAN_INTERVAL, DOMAIN, SENSORS, USER_AGENT

_LOGGER = logging.getLogger(__name__)

# "Quels risques orageux à ALTORF (Bas-Rhin / Alsace) ? ..."
_TITLE_TOWN_RE = re.compile(r"risques orageux à\s+(.*?)\s+\(", re.IGNORECASE)


class KeraunosError(Exception):
    """Raised when the storm-risk page cannot be fetched or parsed."""


def parse_risk(html: str) -> dict[str, str]:
    """Parse the Keraunos storm-risk page into a flat dict.

    Returns a dict with ``town`` plus one entry per key in ``SENSORS``.
    Raises :class:`KeraunosError` when the page does not describe a real commune
    (e.g. an unknown INSEE code yields an empty town in the page title).
    """
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.get_text() if soup.title else ""
    match = _TITLE_TOWN_RE.search(title)
    town = match.group(1).strip().title() if match else ""
    if not town:
        raise KeraunosError("no commune found for this INSEE code")

    # The first BADGE_COUNT `.media-body` spans are the "Aujourd'hui" block, in
    # the fixed order: storm risk, storm probability, hail, tornado.
    badges = [span.get_text(strip=True) for span in soup.select("span.media-body")]
    if len(badges) < BADGE_COUNT:
        raise KeraunosError(
            f"expected {BADGE_COUNT} risk badges, found {len(badges)}"
        )

    data: dict[str, str] = {"town": town}
    for index, key in enumerate(SENSORS):
        data[key] = badges[index]
    return data


class KeraunosCoordinator(DataUpdateCoordinator[dict[str, str]]):
    """Fetch and parse the Keraunos storm-risk page on a schedule."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, insee: str) -> None:
        """Initialise the coordinator for a single commune."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{insee}",
            update_interval=DEFAULT_SCAN_INTERVAL,
            config_entry=entry,
        )
        self.insee = insee
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict[str, str]:
        """Fetch the page and parse it off the event loop."""
        url = BASE_URL.format(code=self.insee)
        try:
            async with self._session.get(
                url, headers={"User-Agent": USER_AGENT}, timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response.raise_for_status()
                html = await response.text()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"error fetching {url}: {err}") from err

        try:
            return await self.hass.async_add_executor_job(parse_risk, html)
        except KeraunosError as err:
            raise UpdateFailed(str(err)) from err
