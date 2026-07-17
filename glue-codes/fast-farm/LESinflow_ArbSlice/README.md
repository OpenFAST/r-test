## LESinflow  (`Mod_AmbWind=1`)
Simulation with one turbine (NREL 5-MW) using precursor VTKs (`Mod_AmbWind=1`).

Velocity outputs are extracted at 2R (1D) and 3R downstream of the turbine (see `OutDist`).

NOTES:
This test case is for testing purposes, for a realistic simulation, consider the following:


- Follow the modeling of guidelines of FAST.Farm (https://openfast.readthedocs.io/en/dev/source/user/fast.farm/ModelGuidance.html)

- Consider using more output radial stations (`OutRadii`)

- Increase the simulation time length (might need to adjust that `NumPlanes` and `NX_Low` as well)

- (typically more output planes are further away from the rotor)
