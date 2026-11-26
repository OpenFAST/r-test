# py_bd_5MW_dynamic

## Purpose

Runs the `bd_5MW_dynamic` module case through the BeamDyn C-bindings interface from Python
(`pyOpenFAST.beamdyn`). The Python driver reads the same BeamDyn driver input file as
`beamdyn_driver`, prescribes the same root motion (rotation about the global origin at a
constant angular velocity), and writes the output channels returned by the interface.
The simulated time is 6 s instead of the 30 s of `bd_5MW_dynamic` to keep the baseline small.

## Files

| File | Description |
|---|---|
| `py_bd_driver.py` | Python driver for the BeamDyn C-bindings interface |
| `bd_driver.inp` | BeamDyn driver input file (as `bd_5MW_dynamic`, with `t_final` = 6 s) |
| `bd_primary.inp`, `beam_props.inp` | BeamDyn primary and beam property input files (as `bd_5MW_dynamic`) |
| `py_bd_driver.out` | Baseline output channels |

## How to run

From a build directory configured with `-DBUILD_TESTING=ON`, with `pyOpenFAST` installed
(`pip install glue-codes/python`):

    ctest -R py_bd_5MW_dynamic

## Expected results

The output channels agree with those of `beamdyn_driver` for the same inputs to single
precision (the interface returns channel values as `c_float`). When the baseline was
generated, the largest relative difference from the `beamdyn_driver` result was 6e-8.

## CTest

`py_bd_5MW_dynamic`, labels `beamdyn;dynamic;python`.
