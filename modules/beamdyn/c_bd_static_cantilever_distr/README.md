# c_bd_static_cantilever_distr

## Purpose

Runs a static solve with a distributed force, a distributed moment, and a tip moment through the BeamDyn C-bindings interface with the C driver `beamdyn_c_binding_driver`, which reads the BeamDyn driver input file. The loads are applied through `BD_C_SetPointLoads` and `BD_C_SetDistrLoads`.

## Files

| File | Description |
|---|---|
| `bd_driver.inp`, `bd_primary.inp`, `beam_props.inp` | `bd_driver.inp` is the `bd_static_cantilever_beam` file with `DistrLoad(1)` = 0.5 N/m, `DistrLoad(5)` = 0.2 N-m/m, and `TipLoad(6)` = 0.3 N-m. `bd_primary.inp` and `beam_props.inp` are copies. |
| `bd_driver.out` | Baseline. `bd_driver.out` was written by `beamdyn_driver` for the same inputs (macOS, gfortran 16, double precision). |

## How to run

From a build directory configured with `-DBUILD_TESTING=ON`:

    ctest -R c_bd_static_cantilever_distr

or directly:

    beamdyn_c_binding_driver bd_driver.inp

## Expected results

The output agrees with `beamdyn_driver` within the regression tolerance. When the case was added the largest relative difference was below 1e-7.

## CTest

`c_bd_static_cantilever_distr`, labels `beamdyn;static`.
