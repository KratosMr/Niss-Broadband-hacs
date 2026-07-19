"""NISS Broadband integration."""
from __future__ import annotations

import logging
from datetime import timedelta

import requests
from bs4 import BeautifulSoup

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_COOKIE_CSRF,
    CONF_COOKIE_IDENTITY,
    CONF_COOKIE_PORTAL,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    HEADERS,
    SENSOR_TYPES,
    UNIT_TO_GB,
    URL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NISS Broadband from a config entry."""
    coordinator = NissDataCoordinator(hass, entry)

    # Do an initial refresh — raises ConfigEntryNotReady on failure
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Re-run setup if the user updates options (e.g. scan interval)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


def parse_usage_value(value_text: str) -> float | None:
    """Parse a usage string like '3.72 GB', '512 MB', or '1.2 TB' into GB."""
    if not value_text or not isinstance(value_text, str):
        return None

    text = value_text.strip().upper()

    multiplier = 1.0  # default: assume GB
    for unit, factor in UNIT_TO_GB.items():
        if unit in text:
            multiplier = factor
            text = text.replace(unit, "").strip()
            break

    try:
        return round(float(text.replace(",", "")) * multiplier, 4)
    except ValueError:
        return None


def fetch_usage(cookies: dict) -> dict[str, str | None]:
    """Blocking HTTP fetch — run in executor."""
    response = requests.get(URL, headers=HEADERS, cookies=cookies, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    result: dict[str, str | None] = {k: None for k in SENSOR_TYPES}

    for card in soup.find_all("div", class_="session-summary-card"):
        label_el = card.find("div", class_="summary-label")
        value_el = card.find("div", class_="summary-value")
        if not label_el or not value_el:
            continue
        label = label_el.get_text(strip=True).lower()
        raw = value_el.get_text(strip=True)
        if "upload" in label:
            result["upload"] = raw
        elif "download" in label:
            result["download"] = raw
        elif "total" in label:
            result["total"] = raw

    return result


class NissDataCoordinator(DataUpdateCoordinator):
    """Fetch and cache NISS usage data on a schedule."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        interval_minutes = entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=interval_minutes),
        )
        self._cookies = {
            "customerportal": entry.data[CONF_COOKIE_PORTAL],
            "_identity-backend-user": entry.data[CONF_COOKIE_IDENTITY],
            "_csrf-backend-user": entry.data[CONF_COOKIE_CSRF],
        }

    async def _async_update_data(self) -> dict[str, float | None]:
        """Fetch data and parse it. Raises UpdateFailed on any error."""
        try:
            raw = await self.hass.async_add_executor_job(fetch_usage, self._cookies)
        except requests.RequestException as err:
            raise UpdateFailed(f"HTTP request failed: {err}") from err

        parsed = {key: parse_usage_value(val) for key, val in raw.items()}

        for key, val in parsed.items():
            if val is None:
                _LOGGER.warning("Could not parse value for '%s': %r", key, raw.get(key))

        return parsed
