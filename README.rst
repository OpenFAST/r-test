r-test
======

This repository serves as a container for regression test data for system-level
and module-level testing of OpenFAST. The repository contains:

- Input files for test case execution
- Baseline solutions for various machine and compiler combinations
- Turbine models used in the regression test cases

The baseline solutions serve as "gold standards" for the regression test suite
and are updated periodically as OpenFAST and it's modules are improved.

Module tests
~~~~~~~~~~~~
A partion of the OpenFAST physics modules contain regression tests. These modules
include a driver-code that runs the module in stand-alone mode rather than coupled
through the OpenFAST glue-code.

The module-level tests are found in ``r-test/modules/``.

Full system tests
~~~~~~~~~~~~~~~~~
The majority of the existing tests are system-level tests for the OpenFAST glue-code and
are found in ``r-test/glue-codes/``.

The tests are realistic cases initially taken from the `GL certification process <https://www.nrel.gov/news/press/2005/357.html>`_
and formerly known as the `FAST V8 CertTests <https://github.com/NWTC/FAST/tree/master/CertTest>`_.
As physics models are changed or improved, we continuously update the tests cases to capture
new features and conform to the new input file specification.
Each test case directory contains the OpenFAST
input file, ``.fst``, and all other case-specific inputs. All turbine-specific
inputs are linked by relative paths to their corresponding turbine data
directory. See the individual test case README's for more information regarding
the particular turbine model and portion of the OpenFAST system that is being
tested.

The included turbine model are listed below.

============== ========================================================================================================================
 Turbine Name   Description and Info
============== ========================================================================================================================
 5MW_Baseline   `NREL offshore 5-MW baseline wind turbine <http://www.nrel.gov/docs/fy09osti/38060.pdf>`_
 AOC            `Atlantic Orient Company 15/50 wind turbine <http://www.nrel.gov/docs/legosti/old/4740.pdf>`_
 AWT27          Advanced Wind Turbine program blade 27
 SWRT           `Small Wind Research Turbine <http://www.nrel.gov/docs/fy06osti/38550.pdf>`__
 UAE_VI         `Unsteady Aerodynamics Experiment research wind turbine <http://www.nrel.gov/docs/fy04osti/34755.pdf>`__
 WP_Baseline    `WindPACT 1.5-MW baseline wind turbine <http://www.nrel.gov/docs/fy06osti/32495.pdf>`__
============== ========================================================================================================================

For reference, a mapping of the legacy CertTest case naming scheme from ``TestNN`` to
the current test names is given below.

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
solutions generated on a series of system and compiler combinations.
Currently, the supported system/compiler combinations for successful
regression testing along with the toolsets use are given below.

================= ======================= ========================= ==================
 System-Compiler   System Version          Compiler                  Math Library
================= ======================= ========================= ==================
 windows-intel     Windows 10 V 2004       Intel OneAPI 2021         Intel MKL 2021
 linux-intel       Ubuntu 20.04 (WSL)      Intel OneAPI 2021         Intel MKL 2021
 linux-gnu         Ubuntu 20.04 (WSL)      GNU Fortran 10.2 (APT)    liblapack (APT)    
 macos-gnu         macOS 10.15.7           GNU Fortran 10.2 (Brew)   `Accelerate <https://developer.apple.com/documentation/accelerate>`_
================= ======================= ========================= ==================

The regression test only supports double precision solutions, so all
baseline solutions are generated with a double precision build.

Updating the baselines
----------------------
The baseline directories can be updated with the included
``updateBaselineSolutions.py``. This script copies locally generated OpenFAST
solutions into the appropriate system - compiler baseline solution directory.

Usage:

.. code-block:: bash

    python updateBaselineSolutions.py source_directory target_directory system_name compiler_id

Example:

.. code-block:: bash

    # Move into the r-test submodule
    cd openfast/reg_tests/r-test

    #       updateBaselineSolutions.py  source_directory                        target_directory     system_name           compiler_id
    #                                                                                                Darwin,Linux,Windows  Intel,GNU
    python  updateBaselineSolutions.py  ../build/reg_tests/glue-codes/openfast  glue-codes/openfast  Linux                 GNU

NOTE: External ServoDyn controllers for 5MW_Baseline cases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The cases using the 5MW turbine require an external controller for ServoDyn.
The source code for three external controllers are provided, but they must be
compiled and installed.

On Linux and Mac, `cmake` projects exist to compile the controllers with
`make`. For Windows systems, `cmake` can generate a Visual Studio project
to compile and install the controllers.

For all system types, create ``build`` directories at

.. code-block:: bash

    r-test/glue-codes/openfast/5MW_Baseline/ServoData/DISCON/build
    r-test/glue-codes/openfast/5MW_Baseline/ServoData/DISCON_ITI/build
    r-test/glue-codes/openfast/5MW_Baseline/ServoData/DISCON_OC3/build

and run ``cmake ..`` in each one. For Windows, add your Visual Studio version and
architecture in the following command:

.. code-block:: bash

  cmake -G "Visual Studio 14 2015 Win64" ..

Ultimately, three ``.dll`` libraries should be compiled and placed in the
``5MW_Baseline`` parallel to the test cases that will be executed. For example,
if the regression test is executed automatically with ``ctest`` or
``manualRegressionTest.py``, all case files will be copied to
``openfast/build``. In this case, these three controller libraries must exist:

.. code-block:: bash

    openfast/build/reg_tests/glue-codes/openfast/5MW_Baseline/ServoData/DISCON.dll
    openfast/build/reg_tests/glue-codes/openfast/5MW_Baseline/ServoData/DISCON_ITIBarge.dll
    openfast/build/reg_tests/glue-codes/openfast/5MW_Baseline/ServoData/DISCON_OC3Hywind.dll
