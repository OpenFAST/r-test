MoorDyn Regression Tests
==================================================================================================================
5MW_OC4 functions as a "normal" r-test with baseline MoorDyn output file from the 5MW_OC4Semi_WSt_WavesWN openFAST
case.

Single_Line_Quasi_Static_Test contains MoorDyn input files for a simple single line chain system. The outputs
from this case can be compared to MoorPy quasi-static tensions/node positions. 

Node_Check_(N=20) and Node_Check_(N=40) set up a single line chain system with 20 nodes vs 40 nodes. The results
from these cases can be compared to check for consistency.


Some code to set up/compare these additional MoorDyn tests is included in MoordynQSchecks.py
