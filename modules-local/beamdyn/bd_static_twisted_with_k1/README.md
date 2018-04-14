Test Name: bd_static_twisted_with_k1
------------------------------------

Twisted beam problem described in Wang et al (2017).

A straight beam is linearly twisted along its primary axis from 0 degrees at the
root to 90 degrees at the tip. A force of 4000 kN is applied at the free end in the 
negative y direction.

Geometric properties

- Height = 0.5 m
- Base = 0.25 m
- Length = 10 m 

Material properties

- Elastic Modulus, E = 200 GPa
- Shear Modulus, G = 79.3 GPa
- Torsion constant is approximately 0.229 * h * b**3 = 0.229 * 0.5 * 0.25**3 = 0.0017890625 (b is the smaller side; for a/b = 2)
-- from https://en.wikipedia.org/wiki/Torsion_constant

Diagonal stiffness matrix entries

- kGA = 8.2604167E+9
- kGA = 8.2604167E+9
- EA = 25.0E+9
- EI_1 = 0.520833E+9
- EI_2 = 0.130208333E+9
- GJ = 0.141872656E+9

Results

Values reported in Wang et al. (2017) (different axes):

BeamDyn -1.132727, -1.715123, -3.578671
ANSYS -1.134192, -1.134192, -3.584232

References

- Wang, Q., Sprague, M.A., Jonkman, J., Johnson, N., Jonkman, B., BeamDyn: a high-fidelity wind turbine blade solver in the FAST modular framework, Wind Energy, DOI: 10.1002/we.2101, 2017.

Last update
2018-03-09 Michael.A.Sprague@nrel.gov