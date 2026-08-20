# 5MW_Land_ADsk_SED_Yaw_CW

Clockwise half of the yawed AeroDisk mirrored-rotor pair. SimplifiedElastoDyn
and AeroDisk, steady 8 m/s, 5 s, fixed rotor speed and fixed nacelle yaw.

This pair exists because the other registered AeroDisk case cannot test the
lateral sign factors at all. AeroDisk assembles its loads in the skew-aligned
disk frame and converts them with

    F = Force(1) x_hat + Force(2) y_hat + Force(3) z_hat

and the same for the moment. In the shipped 5MW table `C_Fy`, `C_Fz`, `C_My`
and `C_Mz` are identically zero across every row, so `Force(2)`, `Force(3)`,
`Moment(2)` and `Moment(3)` are always zero, `z_hat` multiplies nothing, and a
sign error in any of them is invisible. `CpCtCq_Lateral.csv` is the shipped
table with lateral coefficients scaled off the axial ones (`C_Fy = -0.08 C_Fx`,
`C_Fz = 0.05 C_Fx`, `C_My = 0.06 C_Mx`, `C_Mz = -0.04 C_Mx`) so that every
component is non-zero. It is a regression fixture, not a physical rotor.

Why the settings are what they are:

| Setting | Reason |
|---|---|
| `NacYaw = 15` | yaw error, so the skew angle is large and the disk triad is well away from degenerate |
| `YawDOF = False` | yaw held fixed, so the two runs stay exact mirror images of each other |
| `GenDOF = False` | fixed rotor speed; with no controller a free drivetrain would simply run away |
| `CompServo = 0` | nothing in this case needs a controller, and it keeps the comparison deterministic |
| `ShftTilt = -5` | inherited from the baseline; combines with yaw to give a fully three-dimensional skew |
| steady uniform wind | `PLExp = 0`, so the inflow is exactly symmetric about the vertical plane and cannot itself break the mirror |

The nacelle yaw is **+15 here and -15 in the mirrored case**. Yaw acts about the
vertical axis in the inertial frame and is deliberately not a rotor-convention
quantity, so it is not mirrored internally; the mirror image of a turbine yawed
one way is a turbine yawed the other. Giving both cases the same yaw would
compare two machines that are not mirror images.

All 34 AeroDisk channels are requested. The comparison against the mirrored case
is anchored on the inertial-frame loads, which have a frame-independent ground
truth: force is a true vector and moment a pseudovector, so `ADFxi`, `ADFzi` and
`ADMyi` must be identical between the two runs and `ADFyi`, `ADMxi` and `ADMzi`
must be exactly sign-flipped.
