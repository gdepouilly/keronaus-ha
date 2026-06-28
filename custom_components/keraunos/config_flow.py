"""Config and options flow for the Keraunos storm-risk integration."""

from __future__ import annotations

import re
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import BASE_URL, CONF_INSEE, DOMAIN, USER_AGENT
from .coordinator import KeraunosError, parse_risk

INSEE_RE = re.compile(r"^[0-9AB]{5}$", re.IGNORECASE)


async def _validate_insee(hass: HomeAssistant, insee: str) -> str:
    """Fetch the page for ``insee`` and return the resolved town name.

    Raises ``ValueError`` with an error key suitable for the UI.
    """
    insee = insee.strip().upper()
    if not INSEE_RE.match(insee):
        raise ValueError("invalid_format")

    session = async_get_clientsession(hass)
    url = BASE_URL.format(code=insee)
    try:
        async with session.get(
            url, headers={"User-Agent": USER_AGENT}, timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            response.raise_for_status()
            html = await response.text()
    except aiohttp.ClientError as err:
        raise ValueError("cannot_connect") from err

    try:
        data = await hass.async_add_executor_job(parse_risk, html)
    except KeraunosError as err:
        raise ValueError("invalid_insee") from err
    return data["town"]


class KeraunosConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the initial setup: ask for the INSEE code."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Prompt for the commune INSEE code and validate it."""
        errors: dict[str, str] = {}
        if user_input is not None:
            insee = user_input[CONF_INSEE].strip().upper()
            try:
                town = await _validate_insee(self.hass, insee)
            except ValueError as err:
                errors["base"] = str(err)
            else:
                await self.async_set_unique_id(insee)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=town, data={CONF_INSEE: insee})

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_INSEE): str}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> KeraunosOptionsFlow:
        """Return the options flow handler."""
        return KeraunosOptionsFlow()


class KeraunosOptionsFlow(OptionsFlow):
    """Allow changing the commune INSEE code after setup."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Prompt for a new INSEE code and update the entry in place."""
        errors: dict[str, str] = {}
        current = self.config_entry.data[CONF_INSEE]

        if user_input is not None:
            insee = user_input[CONF_INSEE].strip().upper()
            try:
                town = await _validate_insee(self.hass, insee)
            except ValueError as err:
                errors["base"] = str(err)
            else:
                if insee != current:
                    # Guard against pointing two entries at the same commune.
                    for entry in self.hass.config_entries.async_entries(DOMAIN):
                        if entry.entry_id != self.config_entry.entry_id and (
                            entry.unique_id == insee
                        ):
                            errors["base"] = "already_configured"
                            break
                if not errors:
                    self.hass.config_entries.async_update_entry(
                        self.config_entry,
                        title=town,
                        unique_id=insee,
                        data={CONF_INSEE: insee},
                    )
                    return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {vol.Required(CONF_INSEE, default=current): str}
            ),
            errors=errors,
        )
