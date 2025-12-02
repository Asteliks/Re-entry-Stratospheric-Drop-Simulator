import numpy as np

# Material database (example entries)
MATERIALS = {
    'aluminum_6061': {
        'rho': 2700.0,
        'cp': 897.0,
        'latent': 3.0e5,
        'recession_coeff': 1e-6,
        'thermal_conductivity': 167.0,
        'emissivity': 0.2
    },
    'pica': {
        'rho': 240.0,
        'cp': 1250.0,
        'latent': 2.5e6,
        'recession_coeff': 3e-6,
        'thermal_conductivity': 0.3,
        'emissivity': 0.85
    }
}

def fay_riddell_heat_flux(rho, V, Rn):
    # classic Fay-Riddell stagnation-point heating approximation (simplified coefficient)
    return 1.83e-4 * np.sqrt(rho / max(Rn, 1e-6)) * V**3

def ablation_step(state, material_name, dt):
    """Performs one ablation time-step update.
    state dict expects: mass, nose_radius (m), velocity (m/s), altitude (m), surface_temp (K)
    returns updated state and mass_loss (kg)
    """
    mat = MATERIALS[material_name]
    rho = state.get('rho', 1.225 * np.exp(-state['altitude']/8400.0))
    V = state['velocity']
    Rn = max(state.get('nose_radius', 0.01), 1e-4)

    q_dot = fay_riddell_heat_flux(rho, V, Rn)  # W/m2
    # energy balance: q_dot * area -> conduction + reradiation + ablation loss
    A_stag = np.pi * Rn**2
    q_total = q_dot * A_stag  # W

    # radiative loss
    sigma = 5.670374419e-8
    rad_loss = mat['emissivity'] * sigma * (state.get('surface_temp', 300.0)**4) * A_stag

    # conduction into body (very simplified)
    conduction = mat['thermal_conductivity'] * (state.get('surface_temp',300.0) - 300.0) * A_stag / max(Rn,0.001)

    # available energy for ablation
    q_avail = max(q_total - rad_loss - conduction, 0.0)
    m_dot = mat['recession_coeff'] * q_avail / mat['latent']  # kg/s heuristic
    mass_loss = m_dot * dt
    state['mass'] = max(0.0, state['mass'] - mass_loss)
    state['nose_radius'] = Rn + 0.5 * (mass_loss / (mat['rho'] * (np.pi * Rn**2) + 1e-9))
    # update surface temperature (very rough)
    deltaT = q_avail * dt / (mat['rho'] * mat['cp'] * max(1e-6, (A_stag*Rn)))
    state['surface_temp'] = state.get('surface_temp',300.0) + deltaT
    return state, mass_loss
