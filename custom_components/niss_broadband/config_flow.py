"""Config flow for NISS Broadband."""
from __future__ import annotations

import logging

import requests
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_COOKIE_CSRF,
    CONF_COOKIE_IDENTITY,
    CONF_COOKIE_PORTAL,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from . import fetch_usage

_LOGGER = logging.getLogger(__name__)


def _build_cookies(data: dict) -> dict:
    return {
        "customerportal": data[CONF_COOKIE_PORTAL],
        "_identity-backend-user": data[CONF_COOKIE_IDENTITY],
        "_csrf-backend-user": data[CONF_COOKIE_CSRF],
    }


class NissConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial setup UI."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            cookies = _build_cookies(user_input)
            try:
                result = await self.hass.async_add_executor_job(fetch_usage, cookies)
                # If all values are None the cookies are probably wrong
                if all(v is None for v in result.values()):
                    errors["base"] = "cannot_parse"
                else:
                    await self.async_set_unique_id(DOMAIN)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title="NISS Broadband",
                        data=user_input,
                    )
            except requests.exceptions.HTTPError as err:
                _LOGGER.error("HTTP error during setup: %s", err)
                errors["base"] = "invalid_auth"
            except requests.exceptions.ConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during setup")
                errors["base"] = "unknown"

        schema = vol.Schema(
            {
                vol.Required(CONF_COOKIE_PORTAL): str,
                vol.Required(CONF_COOKIE_IDENTITY): str,
                vol.Required(CONF_COOKIE_CSRF): str,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): vol.All(int, vol.Range(min=5, max=1440)),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return NissOptionsFlow(config_entry)


class NissOptionsFlow(config_entries.OptionsFlow):
    """Allow changing the scan interval after setup."""

    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self._config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self._config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        schema = vol.Schema(
            {
                vol.Optional(CONF_SCAN_INTERVAL, default=current_interval): vol.All(
                    int, vol.Range(min=5, max=1440)
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
