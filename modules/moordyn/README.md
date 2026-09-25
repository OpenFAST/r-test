 
MoorDyn Regression Tests
========================

This directory contains test cases for MoorDyn. These test cases are designed to test certain parts of the code as well as coupled behavior between different components. As such, the tests do not always represent physical mooring systems. 

This directory is used by MoorDyn-C to test between the two codes. Changes made here should be coordinated with that project when possible: https://github.com/FloatingArrayDesign/MoorDyn

Test cases are listed alphabetically. Descriptions of the tests can be found below:

**md_5MW_OC4Semi**

Mooring system for OC4-DeepCwind Semi

**md_BdyExtLdDmpg**

A point mass suspended by a line with external force and damping to test MoorDyn's external load and damping capabilities. 

**md_BodiesAndRods**

Body and rod coupled behavior tet with mooring lines. Checks coupled kinematics and hydrodynamics

**md_Single_Line_Quasi_Static_Test**

Compares MoorDyn and MoorPy against eachother for simple single line case. Unused.

**md_VIV**

Catenary riser in a uniform steady flow from validation paper. Frequency of FairTen should be 2.08 Hz

**md_bodyDrag**

A simple test to ensure that body drag coefficients don't go negative in certain orientations

**md_cable**

MoorDyn input file for matching RM3 WEC umbilical cable at 50 m. Lazy-wave dynamic cable with non-zero bending stiffness

**md_case2**

single semi-taut line from VolturnUS-S

**md_case5**

Near vertical line, hitting bottom. Tests line sinking

**md_float**

Buoy model, tests surface piercing pitch decay

**md_horizontal**

Horizontal sinking rod. Line is dummy just to run code

**md_lineFail**

Series of time and tension triggered failures to check moorDyn's failure capabilities.

**md_no_line**

Rod as submerged pendulum

**md_vertical**

Vertical sinking rod. Line is dummy just to run code

**md_viscoelastic**

Single segement viscoelastic test to check mean load dynamic stiffness. Modified version of the viscoelastic test from MD-C polyester tests

**md_syrope**

Single segment Syrope test. Modified version of the viscoelastic test from MD-C Syrope tests

**md_waterkin2**

Testing the hybrid SeaState MD coupling. A vertical line to check the current profile and a rod to check the waves (via submergence), 0.5 submergence = still water level.

**md_waterkin3**

Testing the full SeaState MD coupling.A vertical line to check the current profile and a rod to check the waves (via submergence), 0.5 submergence = still water level. This is the same input file as md_waterkin2 with the excpetion of the waterkinematics flag