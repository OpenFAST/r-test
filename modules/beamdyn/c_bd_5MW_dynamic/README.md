# c_bd_5MW_dynamic

## Purpose

Runs the `bd_5MW_dynamic` module case through the BeamDyn C-bindings interface with the
C driver `beamdyn_c_binding_driver`. Given a single argument, the C driver reads a BeamDyn
driver input file (the input file of `beamdyn_driver`) and writes `bd_driver.out` in the
same format. The simulated time is 6 s instead of the 30 s of `bd_5MW_dynamic` to keep
the baseline small.

## Files

| File | Description |
|---|---|
| `bd_driver.inp` | BeamDyn driver input file (as `bd_5MW_dynamic`, with `t_final` = 6 s) |
| `bd_primary.inp`, `beam_props.inp` | BeamDyn primary and beam property input files (as `bd_5MW_dynamic`) |
| `bd_driver.out` | Baseline: the first 6 s of the `bd_5MW_dynamic` baseline written by `beamdyn_driver` |

## How to run

From a build directory configured with `-DBUILD_TESTING=ON`:

    ctest -R c_bd_5MW_dynamic

or directly:

    beamdyn_c_binding_driver bd_driver.inp

## Expected results

The output agrees with the `beamdyn_driver` baseline within the regression tolerance.
When the case was added, the largest relative difference between the C driver and
`beamdyn_driver` outputs on the same machine was 6e-9.

## CTest

`c_bd_5MW_dynamic`, labels `beamdyn;dynamic`.
