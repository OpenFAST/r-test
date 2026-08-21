Twin-rotor semisubmersible with the second rotor counter-clockwise

From 5MW_MRSemi_DLL_WSt_WavesIrr, with one change:

  MirrorRotor   F F -> F T

It runs OLAF, as the parent does. The free wake was mirrored after this case was
first written, and Wake_Mod has been restored to 3.

This is the case that matters most for the free wake, because OLAF holds every
rotor's wings in one shared wake. Rotor 1 is clockwise and rotor 2 is mirrored,
so the two rotation directions coexist in a single wake and a single Biot-Savart
solve. A mirror implemented by reflecting the world OLAF sees could not do this;
it works because the rotation direction is carried per wing.

Rotor 1 turns clockwise at y = -70 and rotor 2 turns counter-clockwise at
y = +70, so the whole machine maps onto itself under y -> -y: the substructure
joints, the six mooring lines, the five hydrodynamic bodies and the two rotors
are all in mirror pairs or on the plane itself. The wind is steady and uniform
and the waves are long-crested along x, so the environment is uniform in y.

Rotor 2 is therefore the mirror image of rotor 1 within a single solve, sharing
one platform, one sea and one time step. Comparing the two against each other
tests ElastoDyn, SubDyn, HydroDyn, MoorDyn and both controllers at once, with no
run-to-run difference to explain away. The antisymmetric platform response is a
second, sharper check: it must vanish, and it does, to about 1e-6 of the
symmetric response.

The agreement floors at roughly 1e-5 relative. That floor is not the mirror and
not the solver -- tightening ConvTol from 1e-4 to 1e-10 does not move it. The
WAMIT database is itself only symmetric about y to 6.9e-7 relative in the
hydrostatic matrix, and the residual is already present at t = 0 with a
perfectly symmetric structure. Tolerances tighter than about 1e-4 will fail for
that reason rather than for anything to do with rotor direction.
