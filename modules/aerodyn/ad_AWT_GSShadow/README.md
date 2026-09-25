# ad_AWT_GSShadow

Equivalence regression test: the **generalized support (GS) structure** downstream-shadow
influence must reproduce the classic **tower** shadow (Powles) influence when a single GS
member is made geometrically coincident with the tower.

## Setup
- AWT-27 (2-blade **downwind** rotor), standalone `aerodyn_driver`.
- Steady inflow with power-law shear (12 m/s at hub, `PLExp=0.2`); rotor prescribed at
  53.333 rpm, -1 deg pitch. Because the rotor is downwind, each blade passes through the
  tower wake once per revolution; that shadow crossing (plus shear) drives the blade-load
  variation and exercises the unsteady-aero path (`UA_Mod=3`).
- AWT-27 geometry, blade, and airfoils are **referenced** from
  `../../../glue-codes/openfast/AWT27/` (not duplicated).
- The AWT-27 tower is a uniform cylinder (D=0.822368 m, Cd=0.7296 over 0 -> 41.98 m), so a
  single GS member with equal end diameters reproduces it exactly with no taper tweak.
  The shadow (Powles) deficit scales with Cd, so `GSMCd` is set equal to `TwrCd`.

## Two decks (differ only in the shadow source)
- `AeroDyn_TowerRef.dat` - tower model: `TwrShadow=1`, GS off. **Generates the baseline.**
- `AeroDyn.dat` - GS model (the runnable case): tower off, `GSShadow=1`, one GS member
  from joint (0,0,0) to joint (0,0,41.98), D=0.822368, Cd=0.7296.

## Cross-baseline
The committed `ad_driver.outb` baseline is produced by the **tower** deck; the test runs the
**GS** deck. A pass therefore means GS == tower within tolerance.

Regenerate the baseline:
1. Run `aerodyn_driver ad_driver_tower.dvr` (this deck points at `AeroDyn_TowerRef.dat`).
2. Copy the resulting `ad_driver_tower.outb` to `ad_driver.outb`.
