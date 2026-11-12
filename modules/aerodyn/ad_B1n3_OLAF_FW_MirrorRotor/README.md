# One rotating blade, three aerodynamic sections, far wake enabled

Variant of `ad_B1n2_OLAF` with a third blade node (tapered, twisted, so the spanwise circulation is nonuniform), `nNWPanels = 30` and `nFWPanels = 30` (shed vorticity off, so the far wake rolls up and takes the reduced tip/root circulation), so the
near wake fills during the run and far-wake panels are shed: the far-wake
circulation reduction (`PlaceTipRoot`) is exercised, which the base pair never
reaches with `nFWPanels = 0`. Paired clockwise/mirrored to verify the reduction
under `MirrorRotor`.
