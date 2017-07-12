# r-test

This repository serves as a container for regression test data for system level and module level testing of OpenFAST. The repository contains:
- input files for test case execution
- baseline solutions for various machine and compiler combinations
- turbine specific inputs

The baseline solutions serve as "gold standards" for the regression test suite and are updated periodically as OpenFAST and its modules are improved.

## modules-local/beamdyn
These BeamDyn specific cases are configured to run with the BeamDyn driver program rather than with a glue code.

## openfast
These are the system level test cases taken from the [FAST V8 CertTests](https://github.com/NWTC/FAST/tree/master/CertTest).
Each test case directory contains the OpenFAST input file, `.fst`, and all other case specific inputs. All turbine specific inputs are linked by relative paths to their corresponding turbine data directory. See the individual test case README's for more information regarding the particular turbine model and portion of the OpenFAST system that is being tested.

The included turbine directories are:
- 5MW_Baseline - [NREL offshore 5-MW baseline wind turbine](http://www.nrel.gov/docs/fy09osti/38060.pdf)
- AOC - [Atlantic Orient Company 15/50 wind turbine](http://www.nrel.gov/docs/legosti/old/4740.pdf)
- AWT27 - Advanced Wind Turbine program blade 27
- SWRT - [Small Wind Research Turbine](http://www.nrel.gov/docs/fy06osti/38550.pdf)
- UAE_VI - [Unsteady Aerodynamics Experiment research wind turbine](http://www.nrel.gov/docs/fy04osti/34755.pdf)
- WP_Baseline - [WindPACT 1.5-MW baseline wind turbine](http://www.nrel.gov/docs/fy06osti/32495.pdf)

## Baselines
The regression test compares locally generated solutions to the baseline solutions generated on a series of machine and compiler combinations. Currently, the supported machine/compiler combinations for successful regression testing are:
- linux-intel
- macos-gnu
- windows-intel

#### macos-gnu
These results were generated on a MacBook Pro running on macOS Sierra 10.12.4. The OpenFAST binary was compiled with gfortran installed through Homebrew's gcc package at gcc version 6.3.0 (Homebrew GCC 6.3.0_1).

#### linux-intel
These results were generated on [NREL's Peregrine HPC cluster](https://hpc.nrel.gov/users/systems/peregrine) running on Red Hat Enterprise Linux Server release 6.3 (Santiago). The OpenFAST binary was compiled with Intel's ifort compiler version 16.0.2.

#### windows-intel
These results were generated on a Dell Latitude E7440 running Windows 7 Enterprise SP 1. The OpenFAST binary was compiled with Intel's Visual Fortran 17 update 4.

#### Updating the baselines
The baseline directories can be updated with the included `updateBaselineSolutions.py`. This script copies locally generated OpenFAST solutions into the appropriate machine - compiler baseline solution directory.

Usage: `python updateBaselineSolutions.py source_directory target_directory system_name compiler_id`  
Example: `python updateBaselineSolutions.py local/solution/TestName target/solution/TestName [Darwin,Linux,Windows] [Intel,GNU]`

### NOTE - ServoDyn external controllers for 5MW_Baseline cases
The cases using the 5MW turbine require an external controller for ServoDyn. The source code for three external controllers are provided, but they must be compiled and installed. For Linux and Mac systems, a python script is included at `openfast/compileDISCON.py` to configure with `cmake` and compile with `make` automatically. The compile script can be called with this command:  
`python compileDISCON.py compiler_type[gnu,intel] arch_type[32/64]`  
for example:  
`python compileDISCON.py gnu 64`

On Windows systems, `cmake` can generate a Visual Studio project to compile and install the controllers. Create a `build` directory at
- `r-test/openfast/5MW_Baseline/ServoDyn/DISCON/build`
- `r-test/openfast/5MW_Baseline/ServoDyn/DISCON_ITI/build`
- `r-test/openfast/5MW_Baseline/ServoDyn/DISCON_OC3/build`

and run `cmake` in each one replacing your Visual Studio version and architecture in the following command:  
`cmake -G "Visual Studio 14 2015 Win64" ..`

Ultimately, three `.dll`'s should be compiled and placed in the `5MW_Baseline` parallel to the test cases that will be executed. For example, if the regression test is executed automatically with `ctest` or `manualRegressionTest.py`, all case files will be copied to `openfast/build`. In this case, these three controller libraries must exist:
- `openfast/build/reg_tests/openfast/5MW_Baseline/ServoDyn/DISCON.dll`
- `openfast/build/reg_tests/openfast/5MW_Baseline/ServoDyn/DISCON_ITIBarge.dll`
- `openfast/build/reg_tests/openfast/5MW_Baseline/ServoDyn/DISCON_OC3Hywind.dll`
