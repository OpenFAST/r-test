# ad_5MW_GSPotent

Equivalence regression test: the **generalized support (GS) structure** potential-flow
influence must reproduce the classic **tower** potential-flow influence when a single GS
member is made geometrically coincident with the tower.

## Setup
- NREL 5 MW land turbine, standalone `aerodyn_driver`.
- Steady, uniform inflow (8 m/s, `PLExp=0`); rotor prescribed at 9.16 rpm, 0 deg pitch.
  The only unsteadiness is the once-per-revolution support-structure passage, which
  exercises the unsteady-aero blade-load path (`UA_Mod=3`).
- Original 5 MW geometry, blade, and airfoils are **referenced** from
  `../../../glue-codes/openfast/5MW_Baseline/` (not duplicated).
- The tower is made a single clean linear taper (6.000 m -> 3.81174 m over 0 -> 87.6 m);
  only the top tower node diameter differs from the original deck (3.870 m -> 3.81174 m)
  so that one GS member reproduces it exactly.

## Two decks (differ only in the potential-flow source)
- `AeroDyn_TowerRef.dat` - tower model: `TwrPotent=1`, GS off. **Generates the baseline.**
- `AeroDyn.dat` - GS model (the runnable case): tower off, `GSPotent=1`, one GS member
  from joint (0,0,0) D=6.0 to joint (0,0,87.6) D=3.81174.

## Cross-baseline
The committed `ad_driver.outb` baseline is produced by the **tower** deck; the test runs the
**GS** deck. A pass therefore means GS == tower within tolerance.

Regenerate the baseline:
1. Run `aerodyn_driver ad_driver_tower.dvr` (this deck points at `AeroDyn_TowerRef.dat`).
2. Copy the resulting `ad_driver_tower.outb` to `ad_driver.outb`.
