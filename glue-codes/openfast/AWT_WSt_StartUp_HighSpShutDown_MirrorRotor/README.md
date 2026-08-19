# AWT_WSt_StartUp_HighSpShutDown_MirrorRotor

Mirrored counterpart of `AWT_WSt_StartUp_HighSpShutDown`. The `.fst` points at
that case's ElastoDyn, AeroDyn, InflowWind and ServoDyn files rather than
copying them, so the two runs are guaranteed to differ in exactly one setting:
`MirrorRotor = True`.

This is the mirrored-rotor case that puts a controller in the loop. ServoDyn is
completely unmodified and knows nothing about the rotor being reversed — the
signals crossing its boundary are converted into the clockwise convention
instead.

It is chosen for three reasons:

- It operates the **high-speed-shaft brake**, which is the one path where a
  torque is signed by the direction of rotation rather than supplied with a
  sign. The brake deploys at 13 s and takes the rotor down through zero speed
  at about 17 s, so the sign convention is exercised at the moment it matters
  and the `FixHSSBrTq` correction fires.
- The brake is only operated by the **loose-coupling** solve, so `ModCoupling`
  must stay at 1. ElastoDyn has no knowledge of which solver is in use.
- The wind is steady and uniform, so no mirrored turbulence box is needed and
  the comparison is not clouded by a mirrored inflow file.

The turbine is two-bladed, so mirroring leaves the blade order unchanged and
each blade channel compares directly against its own counterpart.

Comparing the two baselines against each other, every channel resolves to
either identical or exactly sign-flipped. The drivetrain quantities the brake
test is about — `RotSpeed`, `RotTorq`, `HSShftTq`, `HSShftPwr`, `HSSBrTq`,
`GenTq` and `GenPwr` — are identical.

Note that a mirror comparison across this case needs a looser tolerance than a
steady one. Bringing the shaft to a halt is a genuine discontinuity, and the
largest residual in both directions falls exactly at the moment the shaft
sticks.
