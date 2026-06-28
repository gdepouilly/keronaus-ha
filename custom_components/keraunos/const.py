"""Constants for the Keraunos storm-risk integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "keraunos"

# Server-rendered storm-risk page for a French commune, keyed by INSEE code.
BASE_URL = "https://www.keraunos.org/site/risque/{code}"

# A desktop User-Agent avoids bot filtering on the upstream site.
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

DEFAULT_SCAN_INTERVAL = timedelta(minutes=30)

CONF_INSEE = "insee"

# Sensor keys, in the order the "Aujourd'hui" badges appear in the page.
# key -> (friendly name, icon)
SENSORS: dict[str, tuple[str, str]] = {
    "risque_orages": ("Risque d'orages", "mdi:weather-lightning"),
    "probabilite_orages": ("Probabilité d'orages", "mdi:weather-lightning-rainy"),
    "probabilite_grele": ("Probabilité de grêle > 5 cm", "mdi:weather-hail"),
    "probabilite_tornade": ("Probabilité de tornade", "mdi:weather-tornado"),
}

# Number of "Aujourd'hui" badges expected; matches len(SENSORS).
BADGE_COUNT = len(SENSORS)
