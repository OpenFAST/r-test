2020.06.15

This is a test case for the OLAF (cOnvecting LAgrangian Filaments) free vortex wake in AeroDyn. This case is not representative of any turbine but rather it is designed to test the vortex wake calculations. The velocity field from a semi-infinite helix is close to constant (close to 1/3) at the inner part of the blade, and has a singular behavior near the tip. 

Example of analytical results are provided in the folder `AnalyticalResults`. 


The following parameters are used:

    U0=10
    Gamma: -232.71056693325  (prescribed, constant along the span)
    R    : 100.0
    Omega: 0.6  rad/s
    Omega: 5.729577951308232 rpm

    a_helix = 0 but a_ll=1/3

    Helical Pitch l   16.6666660    
    Helical Pitch h   104.719757    

The twist of the blade is set to match the helical twist, from 90 deg to 9.46 deg.
