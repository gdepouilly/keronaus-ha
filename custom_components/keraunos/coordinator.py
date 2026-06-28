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

from .const import (
    BADGE_COUNT,
    BASE_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PCT_TO_LEVEL,
    PROBA_COLOR,
    PROBA_RANGES,
    SENSORS,
    SEVERITY_COLORS,
    SEVERITY_LABELS,
    USER_AGENT,
)

_LOGGER = logging.getLogger(__name__)

# "Quels risques orageux à ALTORF (Bas-Rhin / Alsace) ? ..."
_TITLE_TOWN_RE = re.compile(r"risques orageux à\s+(.*?)\s+\(", re.IGNORECASE)
_PREVI_RE = re.compile(r"previ-(\d)")
_TRAIT_RE = re.compile(r"traitProba(\d+)")

# Keys that read the `traitProbaNN` bars, in the order they appear in the pane.
_PROBA_KEYS = [key for key, meta in SENSORS.items() if meta["kind"] == "probability"]


class KeraunosError(Exception):
    """Raised when the storm-risk page cannot be fetched or parsed."""


def _pct_to_level(pct: int) -> int:
    """Map a `traitProbaNN` percentage lower bound to a 0..5 level."""
    if pct in PCT_TO_LEVEL:
        return PCT_TO_LEVEL[pct]
    # Fall back to the highest band whose lower bound is <= pct.
    return max((lvl for bound, lvl in PCT_TO_LEVEL.items() if bound <= pct), default=0)


def parse_risk(html: str) -> dict[str, object]:
    """Parse the Keraunos storm-risk page into a structured dict.

    Returns ``{"town": str, <sensor key>: {"level": int, "description": str, ...}}``
    for each key in ``SENSORS``. Severity entries carry ``label``+``color``;
    probability entries carry ``range``+``color``.

    Raises :class:`KeraunosError` when the page does not describe a real commune
    (e.g. an unknown INSEE code yields an empty town in the page title) or when
    the expected gravity markup is missing.
    """
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.get_text() if soup.title else ""
    match = _TITLE_TOWN_RE.search(title)
    town = match.group(1).strip().title() if match else ""
    if not town:
        raise KeraunosError("no commune found for this INSEE code")

    # Scope to the "Aujourd'hui" pane (the first tab-pane); fall back to the
    # whole document if the layout changes.
    pane = soup.select_one(".tab-pane") or soup
    pane_html = str(pane)

    # Descriptions: the first BADGE_COUNT `.media-body` spans, in fixed order:
    # storm risk, storm probability, hail, tornado.
    descriptions = [s.get_text(strip=True) for s in pane.select("span.media-body")]
    if len(descriptions) < BADGE_COUNT:
        raise KeraunosError(
            f"expected {BADGE_COUNT} risk badges, found {len(descriptions)}"
        )

    # Storm-risk severity from `previ-N`.
    previ = _PREVI_RE.search(pane_html)
    if not previ:
        raise KeraunosError("storm-risk level (previ-N) not found")
    severity = int(previ.group(1))

    # Probability levels from the `traitProbaNN` bars (orages, grêle, tornado).
    proba_levels = [_pct_to_level(int(n)) for n in _TRAIT_RE.findall(pane_html)]
    if len(proba_levels) < len(_PROBA_KEYS):
        raise KeraunosError(
            f"expected {len(_PROBA_KEYS)} probability bars, found {len(proba_levels)}"
        )

    data: dict[str, object] = {"town": town}
    proba_iter = iter(zip(_PROBA_KEYS, proba_levels))
    for index, (key, meta) in enumerate(SENSORS.items()):
        description = descriptions[index]
        if meta["kind"] == "severity":
            data[key] = {
                "level": severity,
                "description": description,
                "label": SEVERITY_LABELS.get(severity, str(severity)),
                "color": SEVERITY_COLORS.get(severity, "#EEEEEE"),
            }
        else:
            _, level = next(proba_iter)
            data[key] = {
                "level": level,
                "description": description,
                "range": PROBA_RANGES.get(level, ""),
                "color": PROBA_COLOR,
            }
    return data


class KeraunosCoordinator(DataUpdateCoordinator[dict[str, object]]):
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

    async def _async_update_data(self) -> dict[str, object]:
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
