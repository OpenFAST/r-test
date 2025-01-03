2024.05

The files here were generated by the Mann generator from DTU for use in the Wake Added Turbulence model (WAT):

The filenames have the form FFDB_D150_512x512x64.u where:
 - FFDB - FAST.Farm database
 - D0150 - nominal rotor diameter of around 150 m
 - 512x512x512
   - 512 grid points in X (direction of propagation)
   - 512 grid points in Y (width)
   - 64  grid points in Z (height)


The Mann box is a zero mean turbulence that can be superimposed on a flow field.  Since the Mann box is periodic in all directions, a single Man box will be repeated across the entire wind farm to provide full coverage of all wakes.

See the user guide for details on the WAT theory, usage, and the input files:
 - https://ap-openfast.readthedocs.io/en/f-ffwat/source/user/fast.farm/InputFiles.html#wake-added-turbulence-wat
 - https://ap-openfast.readthedocs.io/en/f-ffwat/source/user/fast.farm/FFarmTheory.html#wake-added-turbulence-wat
