HydroDyn NBodyMod Test Cases
----------------------------


Background

These cases test the NBodyMod features of HydroDyn, which determine
how the potential-flow hydrodynamics of multiple bodies in a floating
substructure is handled. When HydroDyn is being run with more than
one potential-flow body (NBody > 1), there are three options:

When NBodyMod is set to 1, a single set of potential-flow input data 
is used for the entire set of bodies, meaning coupling terms can be
included. The input data is expected to have 6*NBody load components 
and degrees of freedom.

When NBodyMod is set to 2 or 3, coupling terms between the bodies 
are neglected. In that case, each body will have a corresponding 
set of potential-flow data for its own 6 loads and 6 degrees of freedom. 

NBodyMod=2 expects the potential-flow preprocessing to have have used
bodies centered at the global origin rather than at their displaced and 
rotated locations in the overall support structure. 

NBodyMod=3 expects the potential-flow preprocessing to use bodies that
are already offset at their proper relative positions in the 
substructure.


Test Cases

The test cases in this folder provide a test of each of the three 
NBodyMod options based on the DeepCwind semisubmersible geometry, plus a
more traditional case where the the platform is modeled as a single body. 
The geometry modeled with potential-flow hydrodynamics in these tests 
consists only of the DeepCwind semisubmersible's central column and its
three outside columns (including the thick heave plates at the bottom).
The connective members between these four columns are neglected in the
potential flow preprocessor, which in this case was WAMIT.

When running these test cases, the total loads on the platform (e.g., 
HydroFxi, HydroMxi) should be identical between NBodyMod options 2
and 3, since both neglect couplings. The results of NBodyMod 1 and the
SingleBody case should be identical, since these cases both include
coupling between bodies. Some modest differences can be expected between 
these two pairs of cases due these coupling effects.


WAMIT Preprocessing Inputs

The potential flow data files used in these tests were produced using
WAMIT Version 7.201. The input files for the WAMIT preprocessing runs
are provided in the WAMIT_inputs folder. Its subfolders contain the
GDF files of the meshes for the substructure geometry, as well as the
other input files with the settings that were used. 
