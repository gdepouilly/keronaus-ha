# Keraunos Orages — Home Assistant integration

Displays the per-commune storm-risk forecast from
[Keraunos](https://www.keraunos.org) (Observatoire Français des Tornades et des
Orages Violents) as Home Assistant sensors.

The data is scraped from the server-rendered page
`https://www.keraunos.org/site/risque/{INSEE}` — Keraunos exposes no public JSON
API for these values.

## Sensors

For the configured commune, the integration creates four sensors reflecting the
"Aujourd'hui" (today) block of the page. **Each sensor's state is the
human-readable French text** (e.g. `Risque d'orages forts`). The gravity level
`0`–`5`, official colour and range are exposed as **attributes**, so you can
still build gauges, colour-coding and automations from `level`.

| Sensor | State (text) | Key attributes |
| --- | --- | --- |
| Risque d'orages | `Risque d'orages forts` | `level` (0–5), `level_label` (`aucun`→`extrême`), `color`, `level_max` |
| Probabilité d'orages | `Probabilité modérée d'orages` | `level` (0–5), `probability_range` (e.g. `30 à 45 %`), `color`, `level_max` |
| Probabilité de grêle > 5 cm | `Probabilité très faible…` | `level` (0–5), `probability_range`, `color`, `level_max` |
| Probabilité de tornade | `Probabilité très faible…` | `level` (0–5), `probability_range`, `color`, `level_max` |

Level scale:

- **Risque d'orages** (`previ` severity): `0` aucun · `1` marginal · `2` ordinaire ·
  `3` marqué · `4` sévère · `5` extrême — coloured grey, beige `#e7e5cf`,
  yellow `#FFF479`, orange `#ff8b0f`, red `#FF0000`, magenta `#FF00FF`.
- **Probabilités**: `0` nulle · `1` 5–15 % · `2` 15–30 % · `3` 30–45 % ·
  `4` 45–60 % · `5` >60 %.

The page is polled every 30 minutes.

## Dashboard

Ready-made Lovelace cards are in
[`dashboards/keraunos-gauges.yaml`](dashboards/keraunos-gauges.yaml). Since the
sensor state is text, gauges read the numeric `level` one of two ways:

- **Gauge cards** (built-in, no install) — add a small template sensor that
  exposes `level` as its numeric state, then gauge that (snippet included).
- **Entities card** (built-in) — shows the text directly, level/colour on tap.
- **`custom:gauge-card`** (HACS) — gauges the `level` attribute directly, no
  template sensor needed.
- **Mushroom template chips** (HACS *Mushroom*) — colour-coded by `level`, with a
  card-mod snippet for the exact Keraunos hex colours from the `color` attribute.

Adjust the `sensor.altorf_…` entity ids in the YAML to match your commune.

## Installation

### Manual

Copy the `custom_components/keraunos` folder into your Home Assistant
`config/custom_components/` directory and restart Home Assistant.

### HACS (custom repository)

1. In Home Assistant: **HACS → ⋮ (top right) → Custom repositories**.
2. Repository: `https://github.com/gdepouilly/keronaus-ha` — Category:
   **Integration**.
3. Click **Add**, find **Keraunos Orages** in HACS, and **Download**.
4. **Restart Home Assistant**.

## Configuration

1. Settings → Devices & Services → **Add Integration** → search for
   **Keraunos Orages**.
2. Enter the **5-digit INSEE code** of your commune.
   - You can read it off the Keraunos URL: for
     `…/risque-orage-commune-altorf-67/67008`, the code is `67008`.
   - Corsican communes use `2A###`/`2B###`.
3. The integration validates the code and creates a device named after the
   commune with the four sensors above.

To change the commune later, open the integration's **Configure** (options) and
enter a new INSEE code.

## Notes

- If Keraunos changes its page markup, only `parse_risk()` in
  `custom_components/keraunos/coordinator.py` needs updating.
- Polling every 30 minutes keeps load on keraunos.org negligible.
