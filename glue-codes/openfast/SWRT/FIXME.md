2024.06.28 -- AP

For cases:
 - `SWRT_YFree_VS_EDG01`     (Test15)
 - `SWRT_YFree_VS_EDC01`     (Test16)
 - `SWRT_YFree_VS_WTurb`     (Test17)
set `TFinIndMod=1` when it becomes available.  See GH issue #2290

For later comparison, the FAST7 results are included here: `SWRT_FAST7_results_for_later_AD_fixes`


When FAST8 was introduced, the tail fin option in AeroDyn 15 was not implemented. So this test case has been unstable with AeroDyn and was turned off. Adding the tail fin from the updated AD15 to the model does not give very good agreement with the FAST7 version of this case (CertTest #15). This is most likely due to missing features in the AeroDyn tail fin, most notably that the `TFinIndMod=1` option is not available yet (somewhat related to the FAST7 option of SubAxInd in the furl file).

Despite not matching the FAST7 results very well, we think it best to add these cases as is and note that it should be updated when `TFinIndMod=1` is available. For later comparison, the Test15 results from FAST7 have been added along with this note.
