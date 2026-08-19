# 5MW_Land_BD_noDLL_Steady_MirrorRotor

Mirrored half of the BeamDyn pair. Identical to `5MW_Land_BD_noDLL_Steady_CW`
apart from `MirrorRotor = True` in the `.fst`; the BeamDyn blade file describes
the same clockwise blade and is mirrored internally by the `T M T^T` transform
with `T = diag(1,-1,1,-1,1,-1)`.

Comparing the two baselines against each other, all 105 channels resolve to
identical, exactly sign-flipped, or a mirrored angle. The BeamDyn root and tip
channels are the ones this pair exists to cover: `RootFxr`, `RootFzr`, `RootMyr`,
`TipTDxr`, `TipTDzr` and `TipRDyr` match, while `RootFyr`, `RootMxr`, `RootMzr`,
`TipTDyr`, `TipRDxr` and `TipRDzr` flip.

As with the ElastoDyn pair, these baselines are `.outb` and quantise to roughly
1.5e-5 of channel range, so a mirror comparison made from them should not be run
tighter than about 1e-4.
