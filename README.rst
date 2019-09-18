r-test
======

This repository serves as a container for regression test data for system level
and module level testing of OpenFAST. The repository contains:

- Input files for test case execution
- Baseline solutions for various machine and compiler combinations
- Turbine models used in the regression test cases

The baseline solutions serve as "gold standards" for the regression test suite
and are updated periodically as OpenFAST and its modules are improved.

modules/
~~~~~~~~
This directory contains module level tests for the modules found in the source
code at ``openfast/modules``.

beamdyn/
--------
These BeamDyn specific cases are configured to run with the BeamDyn driver
program rather than with a glue code.

glue-codes/
~~~~~~~~~~~
This directory contains system level tests for the various "glue codes" or
high-level drivers found in the source at ``openfast/glue-codes``.

openfast/
~~~~~~~~~
These are the system level test cases for OpenFAST. This collection of test
cases was adapted from the `FAST V8 CertTests <https://github.com/NWTC/FAST/tree/master/CertTest>`__
and new ones have been added. Each test case directory contains the OpenFAST
input file, ``.fst``, and all other case-specific inputs. All turbine-specific
inputs are linked by relative paths to their corresponding turbine data
directory. See the individual test case README's for more information regarding
the particular turbine model and portion of the OpenFAST system that is being
tested.

The included turbine directories are:

- 5MW_Baseline - `NREL offshore 5-MW baseline wind turbine <http://www.nrel.gov/docs/fy09osti/38060.pdf>`__
- AOC - `Atlantic Orient Company 15/50 wind turbine <http://www.nrel.gov/docs/legosti/old/4740.pdf>`__
- AWT27 - Advanced Wind Turbine program blade 27
- SWRT - `Small Wind Research Turbine <http://www.nrel.gov/docs/fy06osti/38550.pdf>`__
- UAE_VI - `Unsteady Aerodynamics Experiment research wind turbine <http://www.nrel.gov/docs/fy04osti/34755.pdf>`__
- WP_Baseline - `WindPACT 1.5-MW baseline wind turbine <http://www.nrel.gov/docs/fy06osti/32495.pdf>`__

The CertTest cases have renamed from the old style of ``TestNN`` to more
descriptive names. In general, the turbine abbreviation begins the case name
followed by a concise description of the physics involved. A mapping of the
legacy to current names is given below.

======== ========================================
 Legacy   Current
======== ========================================
 Test01   AWT_YFix_WSt
 Test02   AWT_WSt_StartUp_HighSpShutDown
 Test03   AWT_YFree_WSt
 Test04   AWT_YFree_WTurb
 Test05   AWT_WSt_StartUpShutDown
 Test06   AOC_WSt
 Test07   AOC_YFree_WTurb
 Test08   AOC_YFix_WSt
 Test09   UAE_Dnwind_YRamp_WSt
 Test10   UAE_Upwind_Rigid_WRamp_PwrCurve
 Test11   WP_VSP_WTurb_PitchFail
 Test12   WP_VSP_ECD
 Test13   WP_VSP_WTurb
 Test14   WP_Stationary_Linear
 Test15   SWRT_YFree_VS_EDG01
 Test16   SWRT_YFree_VS_EDC01
 Test17   SWRT_YFree_VS_WTurb
 Test18   5MW_Land_DLL_WTurb
 Test19   5MW_OC3Mnpl_DLL_WTurb_WavesIrr
 Test20   5MW_OC3Trpd_DLL_WSt_WavesReg
 Test21   5MW_OC4Jckt_DLL_WTurb_WavesIrr_MGrowth
 Test22   5MW_ITIBarge_DLL_WTurb_WavesIrr
 Test23   5MW_TLP_DLL_WTurb_WavesIrr_WavesMulti
 Test24   5MW_OC3Spar_DLL_WTurb_WavesIrr
 Test25   5MW_OC4Semi_WSt_WavesWN
 Test26   5MW_Land_BD_DLL_WTurb
======== ========================================

Baselines
~~~~~~~~~
The regression test compares locally generated solutions to the baseline
solutions generated on a series of machine and compiler combinations.
Currently, the supported machine/compiler combinations for successful
regression testing are:

- linux-intel
- linux-gnu
- macos-gnu
- windows-intel

The regression test only supports double precision solutions, so all
baseline solutions are generated with a double precision build.

linux-intel
-----------
These results were generated on `NREL's Eagle HPC cluster <https://www.nrel.gov/hpc/eagle-system.html>`__
running on CentOS 7 with Intel Skylake processors. The OpenFAST binary was
compiled with the Intel Fortran compiler at version 18.0.3 and MKL 2018.3.222.

linux-gnu
---------
These results were generated on `NREL's Eagle HPC cluster <https://www.nrel.gov/hpc/eagle-system.html>`__
running on CentOS 7 with Intel Skylake processors. The OpenFAST binary was
compiled with the GNU Fortran compiler at version 7.3.0. The math libraries in
this build are ``openblas`` at version 0.3.6.

macos-gnu
---------
These results were generated on a MacBook Pro running on macOS Sierra 10.12.6.
The OpenFAST binary was compiled with gfortran installed through Homebrew's gcc
package at gcc version 7.2.0 (Homebrew GCC 7.2.0).
The math libraries in this build are found in the
`Accelerate Framework <https://developer.apple.com/documentation/accelerate>`__
installed with Xcode command line tools at version 2347.

windows-intel
-------------
These results were generated on a Dell Latitude E7440 running Windows 7
Enterprise SP 1. The OpenFAST binary was compiled with Intel's Visual Fortran
17 update 4.

Updating the baselines
----------------------
The baseline directories can be updated with the included
``updateBaselineSolutions.py``. This script copies locally generated OpenFAST
solutions into the appropriate machine - compiler baseline solution directory.

Usage:

.. code-block:: bash

    python updateBaselineSolutions.py source_directory target_directory system_name compiler_id

Example:

.. code-block:: bash

    python updateBaselineSolutions.py local/solution/TestName target/solution/TestName [Darwin,Linux,Windows] [Intel,GNU]

NOTE: ServoDyn external controllers for 5MW_Baseline cases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The cases using the 5MW turbine require an external controller for ServoDyn.
The source code for three external controllers are provided, but they must be
compiled and installed.

On Linux and Mac, `cmake` projects exist to compile the controllers with
`make`. For Windows systems, `cmake` can generate a Visual Studio project
to compile and install the controllers.

For all system types, create `build` directories at

- ``r-test/glue-codes/openfast/5MW_Baseline/ServoData/DISCON/build``
- ``r-test/glue-codes/openfast/5MW_Baseline/ServoData/DISCON_ITI/build``
- ``r-test/glue-codes/openfast/5MW_Baseline/ServoData/DISCON_OC3/build``

and run `cmake ..` in each one. For Windows, add your Visual Studio version and
architecture in the following command:

.. code-block:: bash

  cmake -G "Visual Studio 14 2015 Win64" ..

Ultimately, three ``.dll`` libraries should be compiled and placed in the
``5MW_Baseline`` parallel to the test cases that will be executed. For example,
if the regression test is executed automatically with ``ctest`` or
``manualRegressionTest.py``, all case files will be copied to
``openfast/build``. In this case, these three controller libraries must exist:

- ``openfast/build/reg_tests/glue-codes/openfast/5MW_Baseline/ServoData/
  DISCON.dll``
- ``openfast/build/reg_tests/glue-codes/openfast/5MW_Baseline/ServoData/
  DISCON_ITIBarge.dll``
- ``openfast/build/reg_tests/glue-codes/openfast/5MW_Baseline/ServoData/
  DISCON_OC3Hywind.dll``
