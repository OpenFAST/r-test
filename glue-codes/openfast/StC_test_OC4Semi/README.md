## StC\_test\_OC4Semi

This test case illustrates four different Stuctural Controls in use. This is not a realisitic scenario and is only meant as illustrative.

### Model description

OC4 semi-submersible with rigid structure, no contoller, yaw fixed, fixed rotation rate.

### StC locations

- StC at blades
     Point force along blade local `x` direction.  Ramps from 0-4 seconds, steady to 40 seconds, drops to zero.  Loads are unrealisically large.
- StC at nacelle
     Omnidirectional (x-y).  This is not tuned for the structure.
- StC at tower
     TLCD (tuned liquid column damper).  This is not tuned for the structure.
- StC at substructure
      Two vertical StCs located at (0,0,0) and (14,25,0).  These are not tuned for the structure.


### Visualization

The visualization is generated using the vtk output from the simulation (`WrVTK==2` set in the StC\_with\_OC4Semi.fst file).