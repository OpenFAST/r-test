## 5MW_Land_DLL_WTurb_wBlPDyn

This test adds blade pitch dynamics to the `5MW_Land_DLL_WTurb` case by setting the new `PitchDOF` to `True` in ElastoDyn.

Instead of being prescribed by the controller, the pitch motion of the blades is solved dynamically, taking into account both pitch inertia and actuator torque.

The stiffness and damping of the pitch actuators in ServoDyn are tuned to obtain a damped period of 0.5 s and a damping ratio of 0.7.

The results from this case can be compared to those from `5MW_Land_DLL_WTurb` to show the effect of blade pitch and actuator dynamics.
