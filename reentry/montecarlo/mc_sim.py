import numpy as np
from scipy.integrate import solve_ivp
from ..dynamics.six_dof import six_dof_eom

def run_single(initial_state, params, tmax=2000.0):
    sol = solve_ivp(lambda t,y: six_dof_eom(t,y,params), [0,tmax], initial_state, max_step=0.2, rtol=1e-6)
    # find impact when altitude <= 0
    for i in range(sol.y.shape[1]):
        pos = sol.y[0:3,i]
        alt = np.linalg.norm(pos) - 6378137.0
        if alt <= 0:
            x = pos
            r = np.linalg.norm(x)
            lat = np.degrees(np.arcsin(x[2]/r))
            lon = np.degrees(np.arctan2(x[1], x[0]))
            return {'lat': lat, 'lon': lon, 't': sol.t[i]}
    return {'lat': None, 'lon': None, 't': None}

def monte_carlo(initial_state, params, Ns=500, perturb_std=None):
    if perturb_std is None:
        perturb_std = {'v':0.5, 'ang':0.01, 'mass':0.02}
    results = []
    for i in range(Ns):
        st = initial_state.copy()
        st = st.astype(float)
        st[3:6] += np.random.normal(0, perturb_std['v'], 3)
        params2 = params.copy()
        params2['mass'] = params['mass'] * (1.0 + np.random.normal(0, perturb_std['mass']))
        res = run_single(st, params2)
        results.append(res)
    return results
