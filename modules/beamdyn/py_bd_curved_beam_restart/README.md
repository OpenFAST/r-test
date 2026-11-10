# py_bd_curved_beam_restart

## Purpose

Runs a static solve with a tip force, with a checkpoint and restart through the BeamDyn C-bindings interface from Python (`pyOpenFAST.beamdyn`). The loads are applied through `bd_setPointLoads` and `bd_setDistrLoads`. After the fourth load step (t = 0.008 s) the driver writes a checkpoint (`BD_C_PackStates`), ends the library, initializes it again, and restores the checkpoint (`BD_C_UnpackStates`).

## Files

| File | Description |
|---|---|
| `py_bd_driver.py` | Python driver for the BeamDyn C-bindings interface (`checkpoint_time = 0.008`) |
| `bd_driver.inp`, `bd_primary.inp`, `beam_props.inp` | `bd_driver.inp`, `bd_primary.inp`, and `beam_props.inp` are copies of the `bd_curved_beam` inputs. |
| `py_bd_driver.out` | Baseline. `py_bd_driver.out` is a copy of the `py_bd_curved_beam` baseline (the uninterrupted run), so a restart that does not restore the complete state fails the test. The static root reaction is part of the restored state. |

## How to run

From a build directory configured with `-DBUILD_TESTING=ON`:

With `pyOpenFAST` installed (`pip install glue-codes/python`):

    ctest -R py_bd_curved_beam_restart

## Expected results

The restarted run reproduces the uninterrupted run. When the baseline was generated the two outputs were identical to all printed digits.

## CTest

`py_bd_curved_beam_restart`, labels `beamdyn;static;python;restart`.
