# reentry_sim - Re-entry & Stratospheric Drop Simulator (Prototype)

This repository is a research-grade prototype for predicting re-entry / stratospheric
drop footprints with:
- 6-DOF dynamics (translational + rotational)
- Aerodynamic coefficient tables (synthetic CFD sample generator)
- Ablation model based on Fay–Riddell and energy balance (ESA/NASA style)
- Wind profile loader using Open-Meteo API
- Stratosphere-drop example (balloon -> drop)
- Monte-Carlo footprint generation and plotting
- Simple Flask dashboard for visualization
- Dockerfile and GitHub Actions CI workflow

**WARNING:** This is a research prototype. Do **NOT** use for operational safety-critical decisions
without extensive validation and regulatory approvals.
