# 5MW_Land_BD_noDLL_Steady_CW

Clockwise half of the BeamDyn mirrored-rotor pair, matching the operating point of
`5MW_Land_noDLL_Steady_CW` so the two structural models can be cross-checked
against each other.

NREL 5MW land-based with BeamDyn blades, steady 8 m/s, 20 s, free drivetrain, no
controller.

Unlike the ElastoDyn pair this case keeps the default tight coupling.
**BeamDyn is unstable with loose coupling** — it diverges within a few steps. The
gearbox-efficiency direction, which is only reached from the loose-coupling
integrators, is therefore covered by the ElastoDyn pair rather than here.

The mirrored counterpart is `5MW_Land_BD_noDLL_Steady_MirrorRotor`, which differs
only by the `MirrorRotor` flag in the `.fst`.
