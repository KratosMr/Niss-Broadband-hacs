# NISS Broadband for Home Assistant

A custom HACS integration that exposes your [NISS Broadband](https://portal.nissbroadband.com) session usage as Home Assistant sensors.

## Sensors

| Sensor | Description |
|---|---|
| `sensor.niss_upload_data` | Upload usage in GB |
| `sensor.niss_download_data` | Download usage in GB |
| `sensor.niss_total_data` | Total usage in GB |

Values are normalised to GB regardless of whether the portal returns KB, MB, GB, or TB.

---

## Installation via HACS

1. In HACS, go to **Integrations → ⋮ → Custom repositories**
2. Add your repository URL and select category **Integration**
3. Click **Download**
4. Restart Home Assistant

## Manual Installation

Copy the `custom_components/niss_broadband` folder into your HA `config/custom_components/` directory and restart.

---

## Configuration

After restarting, go to **Settings → Devices & Services → Add Integration** and search for **NISS Broadband**.

You will be prompted for three session cookies. To get them:

1. Log in to [portal.nissbroadband.com](https://portal.nissbroadband.com/session-history)
2. Open browser DevTools (`F12`) → **Application** tab → **Cookies**
3. Copy the values for:
   - `customerportal`
   - `_identity-backend-user`
   - `_csrf-backend-user`

> **Note:** Session cookies expire periodically. When your sensors stop updating, return to the integration and reconfigure with fresh cookies via **Settings → Devices & Services → NISS Broadband → Reconfigure**.

You can also set the **update interval** (default: 30 minutes, minimum: 5).

---

## Updating Cookies

Go to **Settings → Devices & Services → NISS Broadband → ⋮ → Reconfigure** and paste new cookie values.
