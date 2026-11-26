# c_bd_curved_beam

## Purpose

Runs a static solve with a tip force through the BeamDyn C-bindings interface with the C driver `beamdyn_c_binding_driver`, which reads the BeamDyn driver input file. The loads are applied through `BD_C_SetPointLoads` and `BD_C_SetDistrLoads`.

## Files

| File | Description |
|---|---|
| `bd_driver.inp`, `bd_primary.inp`, `beam_props.inp` | `bd_driver.inp`, `bd_primary.inp`, and `beam_props.inp` are copies of the `bd_curved_beam` inputs. |
| `bd_driver.out` | Baseline. `bd_driver.out` is the `bd_curved_beam` baseline written by `beamdyn_driver`. |

## How to run

From a build directory configured with `-DBUILD_TESTING=ON`:

    ctest -R c_bd_curved_beam

or directly:

    beamdyn_c_binding_driver bd_driver.inp

## Expected results

The output agrees with `beamdyn_driver` within the regression tolerance. When the case was added the largest relative difference was below 1e-7.

## CTest

`c_bd_curved_beam`, labels `beamdyn;static`.
