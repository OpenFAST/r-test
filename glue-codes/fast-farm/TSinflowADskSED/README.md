## TSinflow (`Mod_AmbWind=2`)
Simulation using two staggered turbines (NREL 5-MW) separated by 3D and with a horizontal offset of 30m, with a turbulent inflow given by one turbsim box (`Mod_AmbWind=2`)


Velocity outputs are extracted at 1R (0.5D) downstream of the turbines (see `OutDist`).


NOTES:
This test case is for testing purposes, for a realistic simulation, consider the following:

- Follow the modeling of guidelines of FAST.Farm (https://openfast.readthedocs.io/en/dev/source/user/fast.farm/ModelGuidance.html)

- Use a realsitic turbine spacing

- Consider using more output radial stations (`OutRadii`)

- Increase the simulation time length (might need to adjust `NumPlanes` and `NX_Low` as well)

- (typically more output planes are further away from the rotor)
