# 5MW_Land_noDLL_Steady_CW

Clockwise half of the mirrored-rotor pair. Identical in every respect to
`5MW_Land_noDLL_Steady_MirrorRotor` except for the `MirrorRotor` flag in the
`.fst`, so the two cases together demonstrate that `MirrorRotor = T` reproduces
the same turbine running counter-clockwise.

NREL 5MW land-based, steady 8 m/s, 20 s. Flexible blades and tower, free
drivetrain, no controller.

Why the settings are what they are:

| Setting | Reason |
|---|---|
| `CompServo = 0` | the ServoDyn interface is not yet supported for mirrored rotors |
| `GenDOF = True` | free drivetrain, so the shaft torque path is actually exercised |
| `ModCoupling = 1` | `SignLSSTrq`, and hence the gearbox efficiency direction, is only reached from the loose-coupling integrators |
| `GBoxEff = 95` | the usual 100% makes both branches of the efficiency factor identical and hides errors in that test |
| `ShftTilt = -5` | inherited from the baseline; gives azimuthal variation so the blades are not interchangeable |

The output list deliberately contains both halves of the shaft-axis channel
split — the rotor-convention names (`RotSpeed`, `RotAccel`, `Azimuth`,
`RotTorq`, `LSShftTq`) and the physical ones (`LSSTipVxa`, `LSSTipAxa`,
`LSSTipPxa`, `LSShftMxa`, `LSSGagMxa`) — since those agree for a clockwise rotor
and differ for a mirrored one.
