# Infinite Helical Wake test case

## Introduction
This is a test case for the OLAF (cOnvecting LAgrangian Filaments) free vortex wake in AeroDyn. 

It is designed to test the vortex wake calculations, and determine the induced velocity field at the lifting line from a "rigid" semi-infinite helix and a straight root vortex.

To achieve such vortex wake system, the wake rollup is disabled (FreeWakeStart = Infinity), resulting in "frozen" wake convecting with the freestream velocity, and the circulation is prescribed to a constant value (CircSolvMethod=3 with Gamma=constant).

This case is not representative of any turbine (**do not use the OLAF input file as is!**).

The velocity field from a semi-infinite helix is close to constant (close to 1/3) at the inner part of the blade, and has a singular behavior near the tip (see reference [1] Chapters 5, 8, 36, 39).
To get results even closer to 1/3, extend the final time TMax to 100s. 

Example of analytical results are provided in the folder `AnalyticalResults`. 

Operating conditions and derivations are provided below.

## Operating conditions

The following operating conditions are specified:

    Wind speed                     :   U0       = 10 [m/s]
    Rotor radius                   :   R        = 100.0 [m]
    Rotational speed               :   Omega    = 0.6 [rad/s] = 5.729577951308232 [rpm]
    Target axial induction at rotor:   a_target = 1/3 [-]
    
## Derived parameters

The helical pitch is the distance run by the wake in one wake rotation [1, chap 8]. 
In this test case, we assume that there is no induction in the wake, the wake convects with
a frozen velocity, forming perfect helices.
Without inductions, the pitch is the free stream times the period of rotation.

    Helical pitch with no induction:   h = U0 T = 2 pi U0 / Omega =  104.719757   [m]
    Helical torsional parameter    :   l = h/(2 pi)               =   16.6666660  [m]  
    
For an infinitely-bladed vortex cylinder the total rotor circulation is [1, chap 5]:

       Gamma_tot = - h gamma_t where gamma_t is the tangential vorticity of the cylinder.

The tangential vorticity is related to the axial induction at the rotor by [1, chap 36]:

       gamma_t/2 = - a U0  [m/s]

Therefore the total rotor ciruclation is:

       Gamma_tot = 2 h a U0

For a 3-bladed rotor (B=3), the circulation per blade to reach the target induction is:

       Gamma = 2 h a_target U0 / B  = 232.71056693325 [m^2/s]

This is the value that is prescribed, constant along the span.

The twist of the blade is set to match the helical twist (see [1, chap 8]):

         tan(twist) = h / (2 pi r)

Resulting in a twist ranging from 90 deg to 9.46 deg.


## References
[1] Branlard (2017) Wind turbine aerodynamics and vorticity-based methods: fundamentals and recent applications, Springer, ISBN: 978-3-319-55163-0
