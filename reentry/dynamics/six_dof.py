import numpy as np
from scipy.spatial.transform import Rotation as R
from .ablation_esa import ablation_step

MU = 3.986004418e14
J2 = 1.08262668e-3
RE = 6378137.0

def gravity_j2(r):
    x,y,z = r
    rnorm = np.linalg.norm(r)
    mu = MU
    a = -mu / rnorm**3 * r
    # J2 correction
    K = 1.5 * J2 * MU * (RE**2) / rnorm**5
    a += K * r * (5*(z**2)/(rnorm**2) - 1)
    return a

def quat_derivative(q, omega):
    # q in scalar-last [x,y,z,w] or [x,y,z,w]? We use scipy Rotation to avoid confusion
    # Here q is [x,y,z,w] as scipy default expects
    wx, wy, wz = omega
    qw = q[3]; qv = np.array(q[:3])
    qdot_v = 0.5*( qw*np.array([wx,wy,wz]) + np.cross(qv, np.array([wx,wy,wz])) )
    qdot_w = -0.5 * np.dot(qv, np.array([wx,wy,wz]))
    return np.hstack([qdot_v, qdot_w])

def six_dof_eom(t, y, params):
    # state vector: pos(3), vel(3), quat(4 x,y,z,w), omega(3)
    pos = y[0:3]
    vel = y[3:6]
    quat = y[6:10]
    omega = y[10:13]

    mass = params['mass']
    inertia = params['inertia']  # 3x3
    aero = params['aero_table']
    Aref = params.get('A_ref', 0.1)
    Lref = params.get('L_ref', 0.5)

    # kinematics
    # atmospheric quantities
    alt = np.linalg.norm(pos) - RE
    rho = params['atm_density'](alt)
    V = np.linalg.norm(vel)
    mach = max(0.01, V / params.get('speed_of_sound', 340.29))

    # approximate angle of attack via body x-axis ~ vel direction in body frame
    r = R.from_quat(quat)
    vel_body = r.inv().apply(vel)
    aoa = np.arctan2(vel_body[2], max(1e-6, vel_body[0]))

    coeffs = aero.coeffs(mach, aoa, np.linalg.norm(omega))
    Cd, Cl, Cm = coeffs['Cd'], coeffs['Cl'], coeffs['Cm']

    qdyn = 0.5 * rho * V**2
    # aerodynamic forces in body frame (X forward, Z down used convention)
    F_drag_body = -Cd * qdyn * Aref * (vel_body / (V + 1e-9))
    F_lift_body = np.array([0.0, Cl * qdyn * Aref, 0.0])

    # moments in body
    M_body = np.array([0.0, Cm * qdyn * Aref * Lref, 0.0])

    # to inertial
    F_inertial = r.apply(F_drag_body + F_lift_body)

    # gravity
    g = gravity_j2(pos)

    acc = F_inertial / mass + g

    # rotational dynamics
    omega_dot = np.linalg.inv(inertia) @ (M_body - np.cross(omega, inertia @ omega))

    qdot = quat_derivative(quat, omega)

    # ablation update (affects mass and shape); called externally typically per dt step
    # we only return derivatives here
    dydt = np.zeros_like(y)
    dydt[0:3] = vel
    dydt[3:6] = acc
    dydt[6:10] = qdot
    dydt[10:13] = omega_dot
    return dydt
