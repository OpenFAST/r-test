# py_bd_curved_beam

## Purpose

Runs a static solve with a tip force through the BeamDyn C-bindings interface from Python (`pyOpenFAST.beamdyn`). The loads are applied through `bd_setPointLoads` and `bd_setDistrLoads`.

## Files

| File | Description |
|---|---|
| `py_bd_driver.py` | Python driver for the BeamDyn C-bindings interface |
| `bd_driver.inp`, `bd_primary.inp`, `beam_props.inp` | `bd_driver.inp`, `bd_primary.inp`, and `beam_props.inp` are copies of the `bd_curved_beam` inputs. |
| `py_bd_driver.out` | Baseline. `py_bd_driver.out` holds the output channels returned by the interface. |

## How to run

From a build directory configured with `-DBUILD_TESTING=ON`:

With `pyOpenFAST` installed (`pip install glue-codes/python`):

    ctest -R py_bd_curved_beam

## Expected results

The output channels agree with `beamdyn_driver` for the same inputs to single precision (channel values are returned as `c_float`). When the baseline was generated the largest relative difference was 3e-6 or less.

## CTest

`py_bd_curved_beam`, labels `beamdyn;static;python`.
