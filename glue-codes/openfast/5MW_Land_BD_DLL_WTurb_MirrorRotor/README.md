# 5MW_Land_BD_DLL_WTurb_MirrorRotor

Mirrored counterpart of `5MW_Land_BD_DLL_WTurb`, and the BeamDyn half of the
turbulent controller pair. See `5MW_Land_DLL_WTurb_MirrorRotor` for why the
InflowWind file is swapped for the `MirrorY` one.

The `.fst` points at the clockwise case's ElastoDyn, AeroDyn and ServoDyn files,
and at the same unmodified `../5MW_Baseline/NRELOffshrBsline5MW_BeamDyn.dat`
blade. The blade input describes the clockwise blade; BeamDyn mirrors it
internally when `MirrorRotor` is set.

This case therefore covers the two hardest pieces at once: a geometrically
exact beam model whose stiffness and mass matrices must be transformed rather
than merely re-signed, and a Bladed-style controller driving it through
turbulence.

Comparing the two baselines against each other, every channel resolves to either
identical or exactly sign-flipped, with the blade root and tip responses
following the same map as the clockwise pair.

The root torsional moments (`B*RootMzr`) need a slightly looser tolerance than
the rest. They are small and stiff, so their own peak makes for a harsh
denominator; the sign map itself is unambiguous.
