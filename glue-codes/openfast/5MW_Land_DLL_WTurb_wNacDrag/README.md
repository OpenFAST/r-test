## 5MW_Land_DLL_WTurb_wNacDrag

This test adds the nacelle drag model to the `5MW_Land_DLL_WTurb` case. The projected areas of the nacelle are calculated based on the nacelle cover geometry estimations from WISDEM's DrivetrainSE module.

The drag parameter Cd for all three directions are set to be 1.0 which is genrally accepted drag coefficient for flow over a cuboid. The position of aerodynamic center of nacelle drag is set to be at the center of the nacelle.

The tower top and tower base loads are expected to be higher than the `5MW_Land_DLL_WTurb` case.