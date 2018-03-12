Test Name: bd_curved_beam
-------------------------

Curved-beam problem described in Bathe and Bolourchi (1979).

Beam lies in the x-z plane with a tip force of 600 lbs acting in the 
positive y direction.  Beam is curved on a radius of 100 inches in the positive 
x direction through a 45 degree arc.

Geometric properties

- Cross section: 1 in x 1 in

Material properties

- Elastic Modulus, E = 10**7 psi
- Poisson Ratio, nu = 0

Diagonal stiffness matrix entries

- kGA = 41.6667E+5
- kGA = 41.6667E+5
- EA = 100.E+5
- EI_1 = 8.333E+5
- EI_2 = 8.333E+5
- GJ = 8.333E+5

Results

Tip displacement reported by Bathe and Bolourchi (1979): 
(-13.4, 53.4, -23.5)

BeamDyn tip displacement reported by Wang et al. (2015): 
(-13.5, 53.4, -23.7)

References

- Bathe, K.-J., Bolourchi, S., Large displacement analysis of three-dimensional beam structures, International Journal for Numerical Methods in Engineering, Vol. 14, 961-986 (1979)
- Wang, Q., Sprague, M., Jonkman, J., Johnson, N., BeamDyn: A high-fidelity wind turbine blade solver in the FAST modular framework, proceedings of SciTech 2015 Kissimmee, Florida, January 5‒9, 2015.   Also published as NREL technical report NREL/CP-5000-63165.

Last update
2018-03-09 Michael.A.Sprague@nrel.gov