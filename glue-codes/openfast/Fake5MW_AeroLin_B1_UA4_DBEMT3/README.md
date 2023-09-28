# Fake 5MW AeroLin

This test case focuses on the linearization of the AeroDynamic models (UA and DBEMT) that have continuous states, with:

 - UA Mod = 4 (4 lin states)
 - DBEMT = 3  (2 second order states per node)
 - UserProp linearization
 - Full inputs linearization

To limit the size of the matrices, the following is done:
  - 4 stations along the blade span is used.
  - 1 blade is used

In addition: 

  - Two tables are introduced in NACA64_A17_2Prop.dat to test the effect of UserProp linearization
  - Blade nodes 2,3,4 use this modified 2 prop airfoil


The A/B/C/D matrices of AeroDyn are the focus here.
