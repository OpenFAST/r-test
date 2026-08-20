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

The list also carries the aerodynamic coefficient and force families at three
blade nodes, together with the per-blade aerodynamic power. These are the
channels that take an explicit mirror sign in `AeroDyn_IO.f90` but were
previously requested by no registered case, so their signs were inferred from
the source rather than measured. Each is paired with its mirror-invariant
partner — `Cy`, `Cm` and `Ct` against `Cl`, `Cd`, `Cx` and `Cn`; `Ft` and `Fy`
against `Fl`, `Fd`, `Fn` and `Fx`; `VIndy` against `VIndx` — so that a sign
applied to the whole group by mistake cannot pass as correct.

`B2AeroPwr` and `B3AeroPwr` require the blade permutation when comparing the two
runs: blade 1 lies on the mirror plane and blades 2 and 3 exchange.
