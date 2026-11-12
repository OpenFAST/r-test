# One rotating blade, two aerodynamic sections, unsteady aero on the wake

Variant of `ad_B1n2_OLAF` with `UA_Mod = 4` and the OLAF advanced option
`DStallOnWake = True`, so the lifting-line circulation is overwritten from the
unsteady-aero Cl each step (`UA_SetGammaDyn`), a path the base pair never
reaches. Paired clockwise/mirrored to verify that circulation carries the
rotation sense under `MirrorRotor`.
