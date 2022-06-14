Subdyn driver tests:

- `AnsysComp1_PinBeam`: Ansys comparison 1, pinned beam with tip-force. This testcase hightlight a bug and is not yet part of the test-suite (loads different on both sides of the joint, see https://github.com/OpenFAST/openfast/issues/855).
- `AnsysComp2_Cable`: Ansys comparison 2, beam with diagonal cable.
- `AnsysComp3_PinBeamCable`: Ansys comparison 3, pinned beam with two diagonal cables.
- `Cable_5Joints`: test of cable elements
- `Force`: test of input loads at given nodes
- `PendulumDamp`: test of rotational joints
- `Rigid`: test of rigid elements
- `Rigid2Interf_Cables`: test rigid links connected to the interface when cables are present. This testcase highlights a bug and is therefore not yet in the test-suite (see https://github.com/OpenFAST/openfast/issues/854).
- `SparHanging`: test of guyan load correction for floating structures
