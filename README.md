# Keraunos Orages — Home Assistant integration

Displays the per-commune storm-risk forecast from
[Keraunos](https://www.keraunos.org) (Observatoire Français des Tornades et des
Orages Violents) as Home Assistant sensors.

The data is scraped from the server-rendered page
`https://www.keraunos.org/site/risque/{INSEE}` — Keraunos exposes no public JSON
API for these values.

## Sensors

For the configured commune, the integration creates four sensors reflecting the
"Aujourd'hui" (today) block of the page:

| Sensor | Example state |
| --- | --- |
| Risque d'orages | `Risque d'orages forts` |
| Probabilité d'orages | `Probabilité modérée d'orages` |
| Probabilité de grêle > 5 cm | `Probabilité très faible de grêle > 5 cm` |
| Probabilité de tornade | `Probabilité très faible de tornade` |

The page is polled every 30 minutes.

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
