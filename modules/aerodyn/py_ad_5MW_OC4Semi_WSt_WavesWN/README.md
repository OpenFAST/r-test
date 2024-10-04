#py\_ad\_5MW\_OC4Semi\_WSt\_WavesWN

This test is based on the fully coupled OpenFAST regression test case 5MW\_OC4Semi\_WSt\_WavesWN. The purpose of this test is to verify that if the same input motions from an OpenFAST test were passed through the c-bindings interface to AeroDyn and InflowWind, the same results would be achieved.

For this test, the 5MW\_OC4Semi\_WSt\_WavesWN case is run with no tower effects, and slightly simplified aero (see the `ad_primary.dat` in this case).  All motions are output for all timesteps from OpenFAST using the `WrVTK` option 3 with all fields.

The resulting vtk motion files are then read in by the simple driver with this test case and used to set all mesh motions passed to AeroDyn through the c-bindings interface from Python.  The resulting aero loads should be exactly identical to the full test case.