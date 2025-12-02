import numpy as np
from scipy.interpolate import RegularGridInterpolator
import os, json

def generate_synthetic_aero_tables(outpath=None):
    """Generate synthetic Cd/Cl/Cm 3D tables (mach x aoa x spin) as example CFD data."""
    mach = np.linspace(0.01, 25.0, 25)
    aoa = np.linspace(-20.0, 20.0, 41) * np.pi/180.0
    spin = np.linspace(0.0, 10.0, 11)
    M, A, S = np.meshgrid(mach, aoa, spin, indexing='ij')
    # synthetic formulas producing plausible shapes
    Cd = 1.0 + 0.3*np.exp(-M/5.0) + 0.8*(np.abs(np.sin(A))) + 0.01*S
    Cl = 0.1 * A * (1 + 0.2*np.tanh(M/3.0))
    Cm = -0.05 * A * (1 + 0.1*S)
    if outpath:
        np.savez(outpath, mach=mach, aoa=aoa, spin=spin, Cd=Cd, Cl=Cl, Cm=Cm)
    return mach, aoa, spin, Cd, Cl, Cm

class AeroTable:
    def __init__(self, mach, aoa, spin, Cd, Cl, Cm):
        self.mach = mach
        self.aoa = aoa
        self.spin = spin
        self.Cd = Cd
        self.Cl = Cl
        self.Cm = Cm
        self.Cd_interp = RegularGridInterpolator((mach, aoa, spin), Cd)
        self.Cl_interp = RegularGridInterpolator((mach, aoa, spin), Cl)
        self.Cm_interp = RegularGridInterpolator((mach, aoa, spin), Cm)

    @classmethod
    def from_synthetic(cls, outpath=None):
        m,a,s,Cd,Cl,Cm = generate_synthetic_aero_tables(outpath)
        return cls(m,a,s,Cd,Cl,Cm)

    def coeffs(self, mach, aoa, spin):
        pt = np.array([mach, aoa, spin])
        Cd = float(self.Cd_interp(pt))
        Cl = float(self.Cl_interp(pt))
        Cm = float(self.Cm_interp(pt))
        return {'Cd': Cd, 'Cl': Cl, 'Cm': Cm}
