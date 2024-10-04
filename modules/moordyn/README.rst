MoorDyn Regression Tests
==================================================================================================================
md_5MW_OC4Semi functions as a "normal" r-test with baseline MoorDyn output file from the 5MW_OC4Semi_WSt_WavesWN openFAST
case.

Single_Line_Quasi_Static_Test contains MoorDyn input files for a simple single line chain system. The outputs
from this case can be compared to MoorPy quasi-static tensions/node positions. 

Other moordyn test cases have been drawn from the MoorDyn-C unit tests.

Some code to set up/compare these additional MoorDyn tests is included in MoordynQSchecks.py (users will need to update paths)

The additional MoorDyn test cases are a work in progress - more test cases and code to analyze them will be added.

This directory is used by MoorDyn-C to test between the two codes. Changes made here should be coordinated with that project
where necessary: https://github.com/FloatingArrayDesign/MoorDyn