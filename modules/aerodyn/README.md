
# Test cases for aerodyn driver


Features:
 - regular analysis, time series analysis, combined cases analyses
 - with or without inflowind
 - basic or advanced rotor inputs
 - OLAF or BEM
 - regular HAWT, or general multi-bladed rotors
 - multiple rotors
 - rotors with no blades and tower only
 - motions: sinusoidal motion of the base, general motion of the base, general motion for yaw, rotor speed and pitch
 -fixed MHK


BEM test cases ("realistic"):

 - ad\_timeseries\_shutdown: NREL5MW rotor, time series analysis, without inflow wind  
 - MultipleHAWT: multiple BAR rotors, regular analysis type, mixed basic/advanced rotor inputs

BEM test cases (feature testing):

 - BAR\_CombinedCases:  BAR rotor, combined case analysis type
 - BAR\_SineMotion: BAR rotor, regular analysis type, sine motion of the base 
 - BAR\_SineMotion\_UA4\_DBEMT3: same as BAR\_SineMotion, but uses continuous formulations for unsteady aerodynamics and DBEMT
 - BAR\_RNAMotion: BAR rotor, regular analysis type, advanced rotor inputs, genereral motion of yaw/pitch and rotor speed, unrealistic case
 - MHK\_RM1\_Fixed: MHK RM1 rotor, regular analysis type, basic rotor inputs, no base motion, cavitation on


OLAF test cases ("realistic"):

 - BAR\_OLAF : BAR rotor, regular analysis type, basic rotor inputs, no inflow wind, realistic setup


OLAF test cases ("analytical"):

 - EllipticalWingInf\_OLAF : one elliptical wing, regular analysis type,  advanced rotor inputs, inflowwind, no wake rollup in OLAF and large time step
 - HelicalWakeInf\_OLAF: "fake" three blades, regular analysis type, advanced rotor inputs, no wake rollup in OLAF


OLAF test cases (for feature testing):

 - VerticalAxis\_OLAF: three bladed H rotor, regular analysis type
 - Kite\_OLAF
 - QuadRotor\_OLAF



