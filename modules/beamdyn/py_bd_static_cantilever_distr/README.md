# py_bd_static_cantilever_distr

## Purpose

Runs a static solve with a distributed force, a distributed moment, and a tip moment through the BeamDyn C-bindings interface from Python (`pyOpenFAST.beamdyn`). The loads are applied through `bd_setPointLoads` and `bd_setDistrLoads`.

## Files

| File | Description |
|---|---|
| `py_bd_driver.py` | Python driver for the BeamDyn C-bindings interface |
| `bd_driver.inp`, `bd_primary.inp`, `beam_props.inp` | `bd_driver.inp` is the `bd_static_cantilever_beam` file with `DistrLoad(1)` = 0.5 N/m, `DistrLoad(5)` = 0.2 N-m/m, and `TipLoad(6)` = 0.3 N-m. `bd_primary.inp` and `beam_props.inp` are copies. |
| `py_bd_driver.out` | Baseline. `py_bd_driver.out` holds the output channels returned by the interface. |

## How to run

From a build directory configured with `-DBUILD_TESTING=ON`:

With `pyOpenFAST` installed (`pip install glue-codes/python`):

    ctest -R py_bd_static_cantilever_distr

## Expected results

The output channels agree with `beamdyn_driver` for the same inputs to single precision (channel values are returned as `c_float`). When the baseline was generated the largest relative difference was 3e-6 or less.

## CTest

`py_bd_static_cantilever_distr`, labels `beamdyn;static;python`.
