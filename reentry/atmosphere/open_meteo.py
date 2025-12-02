import requests
import numpy as np
from datetime import datetime, timezone

def fetch_open_meteo_wind_profile(lat, lon, date_iso=None):
    """Fetch hourly surface wind from Open-Meteo and construct a simple vertical profile.
    Returns dict with 'z' (m), 'u' (m/s east), 'v' (m/s north).
    NOTE: Open-Meteo does not provide full vertical profiles via free endpoint; this function
    synthesizes a reasonable profile using boundary-layer scaling as a placeholder.
    """
    if date_iso is None:
        date_iso = datetime.now(timezone.utc).isoformat()
    url = 'https://api.open-meteo.com/v1/forecast'
    params = {
        'latitude': float(lat),
        'longitude': float(lon),
        'hourly': 'winddirection_10m,windgusts_10m,windspeed_10m',
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        jr = r.json()
        ws = jr.get('hourly', {}).get('windspeed_10m', [0.0])[0]
        wd = jr.get('hourly', {}).get('winddirection_10m', [0.0])[0]
        # synthesize vertical profile: exponential decay of wind with decreasing altitude toward ground
        z = np.concatenate([np.linspace(0,2000,21), np.linspace(2500,80000,39)])
        # base speed increases with altitude to jet-stream like values above ~8km
        u = np.sin(np.deg2rad(wd)) * (ws * (1 + 0.005 * (z/1000)))  # east component
        v = np.cos(np.deg2rad(wd)) * (ws * (1 + 0.005 * (z/1000)))  # north component
        return {'z': z, 'u': u, 'v': v, 'source': 'open-meteo'}
    except Exception as e:
        # fallback: simple calm profile
        z = np.linspace(0,80000,60)
        u = np.zeros_like(z)
        v = np.zeros_like(z)
        return {'z': z, 'u': u, 'v': v, 'source': 'fallback'}
