import numpy as np
from reentry.aerodynamics.aero_tables import AeroTable
from reentry.atmosphere.open_meteo import fetch_open_meteo_wind_profile
from reentry.dynamics.six_dof import six_dof_eom
from reentry.montecarlo.mc_sim import run_single, monte_carlo
from scipy.integrate import solve_ivp

# initial geo-coordinates (Warsaw-ish) at 30 km
lat0, lon0, alt0 = 52.2297, 21.0122, 30000.0
# simple conversion to ECEF (spherical approx)
RE = 6378137.0
phi = np.deg2rad(lat0); lam = np.deg2rad(lon0)
r0 = np.array([ (RE+alt0)*np.cos(phi)*np.cos(lam),
                (RE+alt0)*np.cos(phi)*np.sin(lam),
                (RE+alt0)*np.sin(phi) ])
# assume balloon horizontal velocity ~10 m/s east
v0 = np.array([10.0, 0.0, 0.0])
# quaternion identity (x,y,z,w)
q0 = np.array([0.0, 0.0, 0.0, 1.0])
omega0 = np.array([0.0, 0.0, 0.0])

state0 = np.hstack([r0, v0, q0, omega0])

# assemble parameters
aero = AeroTable.from_synthetic()
params = {
    'mass': 2.0,
    'inertia': np.diag([0.01,0.02,0.03]),
    'aero_table': aero,
    'A_ref': 0.1,
    'L_ref': 0.2,
    'atm_density': lambda h: 1.225 * np.exp(-h/8400.0),
    'speed_of_sound': 340.29
}

print('Running single descent...')
res = run_single(state0, params, tmax=4000.0)
print('Result:', res)

print('Running Monte-Carlo 200 cases...')
mc = monte_carlo(state0, params, Ns=200)
lats = [r['lat'] for r in mc if r['lat'] is not None]
lons = [r['lon'] for r in mc if r['lon'] is not None]
print('Sample impact count:', len(lats))
