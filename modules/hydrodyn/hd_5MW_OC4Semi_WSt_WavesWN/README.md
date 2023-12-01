#hd\_5MW\_OC4Semi\_WSt\_WavesWN


This regression test runs the standalone HydroDyn driver and should produce the same results as the HydroDyn results from the fully coupled regression test.  Note that the SeaState input file is from the seastate/seastate1/ test case.

**Parent regression test:** `openfast/5MW_OC4Semi_WSt_WavesWN/` 


##Steps to reproduce

1. Run the parent regression test with the following:
	- Output every timestep
	- Add all HydroDyn channels (below)
	- Set output format `OutFmt` to `"E15.7E2"` in main `.fst` file
2. Extract the following channels in order from the `.out` file to create `OpenFAST_DisplacementTimeseries.dat`.  These channels are the platform reference point motions, velocities, and accelerations.  The `hydrodyn_driver` code will use these as input to the module in standalone.
	- 'Time'
   - 'B1Surge'
   - 'B1Sway'
   - 'B1Heave'
   - 'B1Roll'
   - 'B1Pitch'
   - 'B1Yaw'
   - 'B1TVxi'
   - 'B1TVyi'
   - 'B1TVzi'
   - 'B1RVxi'
   - 'B1RVyi'
   - 'B1RVzi'
   - 'B1TAxi'
   - 'B1TAyi'
   - 'B1TAzi'
   - 'B1RAxi'
   - 'B1RAyi'
   - 'B1RAzi'
3. Run the standalone HydroDyn regression test with the following
   - Add all HydroDyn channels
   - Set the `OutSwitch` to `1` to output to module level output file
4. Compare the resulting `.out` file from the OpenFAST regression test to the `driver.HD.out` file produced here.



##HydroDyn channels

Add these channels to the parent regression test prior to running that test. See the `OutListParameters.xlsx` document for the channel definitions.

   - "HydroFxi"
   - "HydroFyi"
   - "HydroFzi"
   - "HydroMxi"
   - "HydroMyi"
   - "HydroMzi"
   - "B1Surge"
   - "B1Sway"
   - "B1Heave"
   - "B1Roll"
   - "B1Pitch"
   - "B1Yaw"
   - "B1TVxi"
   - "B1TVyi"
   - "B1TVzi"
   - "B1RVxi"
   - "B1RVyi"
   - "B1RVzi"
   - "B1TAxi"
   - "B1TAyi"
   - "B1TAzi"
   - "B1RAxi"
   - "B1RAyi"
   - "B1RAzi"
   - "WavesFxi"
   - "WavesFyi"
   - "WavesFzi"
   - "WavesMxi"
   - "WavesMyi"
   - "WavesMzi"
   - "HdrStcFxi"
   - "HdrStcFyi"
   - "HdrStcFzi"
   - "HdrStcMxi"
   - "HdrStcMyi"
   - "HdrStcMzi"
   - "RdtnFxi"
   - "RdtnFyi"
   - "RdtnFzi"
   - "RdtnMxi"
   - "RdtnMyi"
   - "RdtnMzi"


##Notes on settings

- Insuffucient precision in the output of either the parent regression test or this regression test will result in squared off curves due to rounding in the outputs.  To correct this, change the output format as noted above
- use `RANLUX` for `WaveSeed2` in the HydroDyn input files to ensure the same wave seeds are used in both simulations
