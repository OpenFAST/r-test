## StC\_test\_OC4Semi\_Linear\_Tow

This test case checks linearization with a simple tower based structural control in ServoDyn.

This test case should yield exactly the same results as test case StC\_test\_OC4Semi\_Linear\_Nac

### Model description

OC4 semi-submersible with rigid structure, no contoller, yaw fixed, fixed rotation rate, only pitch and StC DOFs enabled.

### StC locations

- StC at tower
     A simple StC is mounted at the tower top (87.6 m above msl) with only the X DOF enabled.  The tower top is where the yaw bearing is located, which is the Z reference for the Nacelle.

### Results

For this test, the following results are expected from frequency analysis:

| Mode | NatFreq\_[Hz] | Damp\_Ratio\_[-] |
| ---- | ------------ | --------------- |
|  1   |   0.050      |   0.01581       |

