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
# "severity" sensors read the `previ-N` storm-risk scale; "probability" sensors
# read the `traitProbaNN` percentage bars.
SENSORS: dict[str, dict[str, str]] = {
    "risque_orages": {
        "name": "Risque d'orages",
        "icon": "mdi:weather-lightning",
        "kind": "severity",
    },
    "probabilite_orages": {
        "name": "Probabilité d'orages",
        "icon": "mdi:weather-lightning-rainy",
        "kind": "probability",
    },
    "probabilite_grele": {
        "name": "Probabilité de grêle > 5 cm",
        "icon": "mdi:weather-hail",
        "kind": "probability",
    },
    "probabilite_tornade": {
        "name": "Probabilité de tornade",
        "icon": "mdi:weather-tornado",
        "kind": "probability",
    },
}

# Number of "Aujourd'hui" description badges expected.
BADGE_COUNT = len(SENSORS)

# All gravity values run 0..5.
LEVEL_MAX = 5

# Storm-risk severity scale (`previ-N`): official labels and colours
# (resolved from the Keraunos stylesheet CSS variables).
SEVERITY_LABELS: dict[int, str] = {
    0: "aucun",
    1: "marginal",
    2: "ordinaire",
    3: "marqué",
    4: "sévère",
    5: "extrême",
}
SEVERITY_COLORS: dict[int, str] = {
    0: "#EEEEEE",
    1: "#e7e5cf",
    2: "#FFF479",
    3: "#ff8b0f",
    4: "#FF0000",
    5: "#FF00FF",
}

# Probability bars (`traitProbaNN`): the NN is the percentage lower bound.
PCT_TO_LEVEL: dict[int, int] = {0: 0, 5: 1, 15: 2, 30: 3, 45: 4, 60: 5}
PROBA_RANGES: dict[int, str] = {
    0: "0 %",
    1: "5 à 15 %",
    2: "15 à 30 %",
    3: "30 à 45 %",
    4: "45 à 60 %",
    5: "> 60 %",
}
PROBA_COLOR = "#E30613"
