# 5MW_Land_noDLL_Steady_MirrorRotor

Mirrored half of the mirrored-rotor pair. Identical to
`5MW_Land_noDLL_Steady_CW` apart from `MirrorRotor = True` in the `.fst` — the
ElastoDyn, AeroDyn, blade and airfoil inputs all describe the same clockwise
turbine, and the mirror is applied internally.

See the clockwise case for why the settings are what they are.

Comparing the two baselines against each other, every channel resolves to one
of: identical, exactly sign-flipped, or a mirrored angle. Channels named after a
rotor or drivetrain quantity (`RotSpeed`, `RotTorq`, `Azimuth`, `HSShftTq`,
`RotPwr`, `RotThrust`) are identical; channels carrying an explicit axis suffix
(`LSShftMxa`, `LSSTipVxa`, `LSSTipAxa`, `LSSGagMxa`) are sign-flipped, as are
the lateral forces and the in-plane blade responses. `LSSTipPxa` is a mirrored
angle.

Note that these baselines are stored as `.outb`, which packs each channel into
int16 and so quantises to roughly 1.5e-5 of the channel range. A mirror
comparison made from these files should not be run tighter than about 1e-4, or
it measures the file format rather than the physics.
