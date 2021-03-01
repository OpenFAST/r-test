# Test of joints - pendulum with forced oscillations

```
   I (interface)
   |
   o (pin joint)
   \
    \
     \
``` 

The interface in undergoing oscillations at a fixed frequency, with increasing amplitude

Gravity is not included.

Gravity and extra moment have no effect on the displacements because the "ExtraMoment" only considers the Guyan motion, and in that case the Guyan motion is a pure translation along x. 
The rotation is taken care by the CB modes.

The case was also run in OpenModellica for comparison


A stiff case is also provided, in which case the whole structure translates as a rigid body, following the interface motion




