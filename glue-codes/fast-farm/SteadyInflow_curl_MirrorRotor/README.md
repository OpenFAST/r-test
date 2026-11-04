# SteadyInflow_curl_MirrorRotor

A counter-rotating two-turbine farm: turbine 1 is clockwise, turbine 2 is the
same deck with `MirrorRotor = T`, placed at y = +60 m and y = -60 m (0.95 D
apart, so the wakes interact downstream) with fixed nacelle yaws of +8 and
-8 degrees. The inflow is steady and sheared (8 m/s at 90 m, power-law 0.2)
through one InflowWind instance, the wake model is curled (`Mod_Wake = 2`)
with swirl on, and wake-added turbulence is off. The rotors are fixed-speed
(`GenDOF = False`), as in the other FFTest decks; the rotation-sense coupling
is carried by the aerodynamic torque, not the drivetrain.

The whole farm maps onto itself under y -> -y, so beyond the regression
comparison this case asserts a symmetry: every turbine-2 quantity must be the
mirror image of its turbine-1 partner under the measured sign map (even
channels equal, odd channels opposite, the skew azimuth supplementary, the
wake swirl reversed). `reg_tests/otherTests/farm_mirror_pair.py --twin <run>`
performs that check and is run by `run_guards.sh`.

Measured floors when the case was created (2026-11-03, see
`FASTFARM_MIRROR_PLAN.md` in the project scratch): all farm and turbine
channels pair to better than 2e-3 relative; the wake-plane transverse
velocity fields pair to 1.5e-2 relative, a floor set by the one-sided vortex
line in `AddVelocityCurl` (`do ir = 2, nVortex-1`), which is an upstream
discretisation asymmetry visible for any pair of oppositely yawed rotors and
is unrelated to `MirrorRotor`.

The yaw angles matter: with no yaw and no shaft tilt the skew angle is
numerical noise (~0.02 deg), the curled vortices and swirl are never
energised, and the case could not fail on the one quantity that carries the
rotation sense.
