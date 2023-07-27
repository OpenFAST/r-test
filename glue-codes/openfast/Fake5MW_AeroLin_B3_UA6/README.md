# Fake 5MW AeroLin

This test case focuses on the linearization of the Oye UA model, with:

 - UA Mod = 6 (Oye, 1 state)
 - UserProp linearization
 - 3 blade are used
 - The value `T_f0` in the `NACA64_A17_2Prop.dat` airfoil file is increased to 30 to further affect the Oye UA model


To limit the size of the matrices, the following is done:
  - 4 stations along the blade span is used.
  - Only the basic inputs are used

In addition: 

  - Two tables are introduced in `NACA64_A17_2Prop.dat` to test the effect of UserProp linearization
  - Blade nodes 2,3,4 use this modified 2 prop airfoil


The A/B/C/D matrices of AeroDyn are the focus here.
