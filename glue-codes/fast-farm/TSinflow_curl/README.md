## TSinflow curl (`Mod_AmbWind=2` and `Mod_Wake=2`) 
Simulation using two staggered turbines (NREL 5-MW) separated by 3D and with a horizontal offset of 30m, with a turbulent inflow given by one turbsim box (`Mod_AmbWind=2`).

The first turbine undergoes a yaw maneuver from 0 to 30 deg at the begining of the simulation (see the ServoDyn input file of turbine 1).
The curled-wake model is used for both turbines.

Different instantaneous and time-filtered variables are written to disk (skew angles, average Ct, ambient wind, curled-wake circulation).

NOTES:
This test case is for testing purposes, for a realistic simulation, consider the following:

- Follow the modeling of guidelines of FAST.Farm (https://openfast.readthedocs.io/en/dev/source/user/fast.farm/ModelGuidance.html)

- Use a realsitic turbine spacing

- Consider using more output radial stations (`OutRadii`)

- Increase the simulation time length (might need to adjust `NumPlanes` and `NX_Low` as well)

