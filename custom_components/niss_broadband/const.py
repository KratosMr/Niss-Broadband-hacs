"""Constants for the NISS Broadband integration."""

DOMAIN = "niss_broadband"

# Config entry keys (what the user enters in the UI)
CONF_COOKIE_PORTAL = "cookie_portal"
CONF_COOKIE_IDENTITY = "cookie_identity"
CONF_COOKIE_CSRF = "cookie_csrf"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 30  # minutes

URL = "https://portal.nissbroadband.com/session-history"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://portal.nissbroadband.com/session-history",
}

SENSOR_TYPES = ("upload", "download", "total")

SENSOR_ICONS = {
    "upload": "mdi:upload-network",
    "download": "mdi:download-network",
    "total": "mdi:network",
}

# Multipliers to convert each unit to GB
UNIT_TO_GB: dict[str, float] = {
    "TB": 1024.0,
    "GB": 1.0,
    "MB": 1.0 / 1024,
    "KB": 1.0 / (1024 ** 2),
}
