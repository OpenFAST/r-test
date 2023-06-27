# Tailfin/Tailfurl - 1DOF - Free Yawing under aerodynamic force

## Summary
One degree of freedom system (TFurl only) modeling an isolated tailfin/tailfurl.  The tailfurl axis is aligned with the yaw axis.  The only inertia is in the tailfurl. Only the lift force is considered and a linear lift coefficient is assumed. The tailfin is started with a 10 deg angle.

The relevant parameters are:

```python
    J  = 30000   # Total inertia of the tailfin  [kg m^2]
    r = 10       # Distance between the yawing axis to the tailfin reference point/aerodynamic center [m]
    Area = 1     # Area of the tailfin [m^2]
    U0 = 10      # Wind speed [m/s]
    rho = 1.225  # Air density [kg/m^3]
    Clalpha=2*pi # Slope of the lift coefficient [-]
```

A Python script performing the time integration of the linear and nonlinear model and comparison with OpenFAST results is provided in this directory.


## Description
We consider a wind vane rotating around the inertial axis $z$. All the inertia is concentrated in the Tailfin, with value $J$ with respect to the vertical axis and at the nacelle origin/tower-top point.
We adopt polar coordinates to indicate the location of the tailfin center of mass (assumed to coincide with the aerodynamic reference point of the tailfin), with unit axes:
$\boldsymbol{\hat{r}}$
and
$\boldsymbol{\hat{\theta}}$, where the radial vector is directed along the inertial $x$ axis when $\theta=0$. 
The position of the tailfin center of mass is assumed to be $\boldsymbol{\hat{r}}$, where $r$ is the distance from the vertical axis to the tailfin center of mass.
The relative wind, assuming a freestream of norm $U_0$ along $\boldsymbol{\hat{x}}$ and no induced velocity, is: 

$$ \boldsymbol{V}_\text{rel}= U_0  \boldsymbol{\hat{x}} - r \dot{\theta} \boldsymbol{\hat{\theta}} = U_0 \cos\theta \boldsymbol{\hat{r}} - \left(U_0\sin\theta + r \dot{\theta}\right) \boldsymbol{\hat{\theta}}$$


In the equations below, we present first the nonlinear form and then the linear form (assuming small angles). The angle of attack is:

$$ \alpha = -\arctan \frac{\left(U_0\sin\theta + r \dot{\theta}\right)}{U_0 \cos\theta} \approx -\theta -\frac{r}{U_0}\dot{\theta} $$



We assume that only the lift force is present (and for linearization purposes, we assume a linear lift coefficient with a zero angle of attack at zero lift):

$$ L = \frac{1}{2}\rho V_\text{rel}^2 A C_l(\alpha) \approx  \frac{1}{2}\rho U_0^2 A C_{l,\alpha} \alpha   \approx  -\frac{1}{2}\rho U_0^2 A C_{l,\alpha} \left[\theta +\frac{r}{U_0}\dot{\theta} \right] $$

The moment about the axis is $L\cos\alpha$, leading to the following nonlinear equation of motion:


   $$J \ddot{\theta} = r L \cos\alpha \approx r L$$

Following the approximations introduced above, the linearized equation of motion about $(\theta,\dot\theta)=(0,0)$ is :

   $$J \ddot{\theta} + k \theta  + k \frac{r}{U_0} \dot{\theta} = 0, \qquad  k= \frac{1}{2}\rho U_0^2 A C_{l,\alpha} r $$

