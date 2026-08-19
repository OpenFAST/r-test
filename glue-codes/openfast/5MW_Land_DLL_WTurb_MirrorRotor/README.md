# 5MW_Land_DLL_WTurb_MirrorRotor

Mirrored counterpart of `5MW_Land_DLL_WTurb`. The `.fst` points at that case's
ElastoDyn, AeroDyn and ServoDyn files rather than copying them, so the two runs
differ in exactly two things:

- `MirrorRotor = True`;
- the InflowWind file is `NRELOffshrBsline5MW_InflowWind_12mps_MirrorY.dat`,
  which reads a `y`-reflected copy of the same turbulence box.

The second is necessary because mirroring the flag mirrors the **turbine**, not
the environment. A turbulence box is not symmetric about the rotor axis, so
reproducing the mirror image of the clockwise simulation needs the box reflected
too. `90m_12mps_twr_MirrorY.bts` is `90m_12mps_twr.bts` with the `y` grid
reversed and the lateral velocity component negated.

This is the case that exercises a **real controller**. The Bladed-style DISCON
library is used completely unchanged — same binary, same `DISCON.IN` — because
everything crossing the ServoDyn boundary is presented in the clockwise
convention. Nothing in the controller knows the rotor has been reversed.

Comparing the two baselines against each other, every channel resolves to either
identical or exactly sign-flipped. In particular `BldPitch1`, `GenTq`, `GenPwr`,
`GenSpeed`, `RotSpeed`, `Azimuth` and `RotTorq` are identical, which is the
point: the controller does the same thing on both machines.
