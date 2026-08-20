# 5MW_Land_ADsk_SED_Yaw_MirrorRotor

Mirrored half of the yawed AeroDisk pair. Identical to
`5MW_Land_ADsk_SED_Yaw_CW` apart from `MirrorRotor = True` in the `.fst` and the
sign of `NacYaw` in the SimplifiedElastoDyn input. It shares the clockwise
case's AeroDisk input and coefficient table, which are used verbatim.

See the clockwise case for why the settings are what they are, and in particular
for why the yaw angle is reversed rather than repeated.

Measured against the clockwise case, every channel resolves. In the disk frame
all three force components are identical and all three moment components are
sign-flipped, which is what taking components against a triad whose basis
vectors all mirror as true vectors requires. In the inertial frame `ADFxi`,
`ADFzi` and `ADMyi` are identical and `ADFyi`, `ADMxi` and `ADMzi` are
sign-flipped.
