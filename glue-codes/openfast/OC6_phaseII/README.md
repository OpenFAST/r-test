## OC6\_phaseII\_SoilDyn

This test case illustrates use of SoilDyn to specify a soil stiffness matrix for use by SubDyn. If the soil stiffness is linear then it can be specified directly in SubDyn, so this case is used to show that SoilDyn is functioning.

### Model description

OC6 Monopile as described in [https://doi.org/10.1002/we.2698](https://doi.org/10.1002/we.2698).

### Matrix Comparison

The same soil stiffness matrix that is specified in [OC6_phaseII_SoilDyn.dat](OC6_phaseII_SoilDyn.dat) is also given in [OC6_phaseII_Monopile_SSI.dat](OC6_phaseII_Monopile_SSI.dat) which can be referenced in [OC6_phaseII_Monopile_SubDyn.dat](OC6_phaseII_Monopile_SubDyn.dat) by adding `"OC6_phaseII_Monopile_SSI.dat"` to line 55. 