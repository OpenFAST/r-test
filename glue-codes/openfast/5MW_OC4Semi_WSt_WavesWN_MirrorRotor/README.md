# 5MW_OC4Semi_WSt_WavesWN_MirrorRotor

Mirrored counterpart of `5MW_OC4Semi_WSt_WavesWN`. The `.fst` points at that
case's ElastoDyn, AeroDyn, ServoDyn, SeaState, HydroDyn and MoorDyn files rather
than copying them, so the two runs differ only in `MirrorRotor`.

This is the case that shows the mirror composing with the full offshore stack:
hydrodynamics, sea state, mooring and the platform degrees of freedom, under
tight coupling, with an unmodified Bladed-style controller.

It is a stronger test than it first appears. The sea state is genuinely
mirror-symmetric — `WaveDir = 0` with `WaveDirMod = 0` gives a long-crested wave
train travelling along `x` that is uniform in `y` — and the OC4 DeepCwind semi's
three columns and three mooring lines at 120 degrees map onto themselves under
the reflection. So this is a complete mirror rather than a check that the run
merely stays stable.

Mooring line 2 lies on the mirror plane, so it maps to itself and **lines 1 and
3 swap**. Note that this is the opposite arrangement to the blades, where it is
blade 1 that lies on the plane and blades 2 and 3 swap. `FairTen1` of the
mirrored run corresponds to `FairTen3` of the clockwise one.

Comparing the two runs within a single build, every channel resolves to either
identical or exactly sign-flipped, with nothing left over.

Comparing the two stored baselines is looser, because the clockwise baseline
predates this work and was produced by a different build. Re-running the
clockwise case with a current build differs from its own stored baseline by a
median of 1.3e-4 and a maximum of 2.6e-3, and those same figures reappear in the
pair comparison channel for channel. A mirror comparison made from these two
files therefore measures the build difference once it is tightened much below
5e-3; it is not measuring the mirror.
