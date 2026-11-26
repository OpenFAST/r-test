# py_bd_5MW_dynamic_restart

## Purpose

Checks the checkpoint and restart of the BeamDyn C-bindings interface. The case is
`py_bd_5MW_dynamic` with one difference: at t = 3 s the Python driver writes a checkpoint
file (`BD_C_PackStates`), ends the library, initializes it again from the same input
files, restores the checkpoint (`BD_C_UnpackStates`), and continues to the end time.

## Files

| File | Description |
|---|---|
| `py_bd_driver.py` | Python driver; same as in `py_bd_5MW_dynamic` with `checkpoint_time = 3.0` |
| `bd_driver.inp`, `bd_primary.inp`, `beam_props.inp` | Same as `py_bd_5MW_dynamic` |
| `py_bd_driver.out` | Baseline output channels: a copy of the `py_bd_5MW_dynamic` baseline |

## How to run

From a build directory configured with `-DBUILD_TESTING=ON`, with `pyOpenFAST` installed
(`pip install glue-codes/python`):

    ctest -R py_bd_5MW_dynamic_restart

## Expected results

The restarted run reproduces the uninterrupted run. The baseline is the output of the
uninterrupted run, so a restart that does not restore the complete state fails the test.
When the baseline was generated, the restarted and uninterrupted outputs were identical
to all printed digits.

## CTest

`py_bd_5MW_dynamic_restart`, labels `beamdyn;dynamic;python;restart`.
