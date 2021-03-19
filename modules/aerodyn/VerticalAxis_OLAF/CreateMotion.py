import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# Local 
import weio


# --- Rot Motion
RPM  = 60
tMax = 35
dt   = 0.5
tRamp =3


time  = np.arange(0,tMax+dt/2,dt)
omega = np.ones(time.shape)*RPM/60*2*np.pi
ramp  = np.linspace(0,1, int(tRamp/dt))
omega[0:len(ramp)] *= ramp
azimuth = np.cumsum(omega*dt)
rotacc  = np.concatenate(([0], np.diff(omega)/dt))
data    = np.column_stack((time, azimuth, omega, rotacc))
df = pd.DataFrame( data=data, columns=['time_[s]', 'azimuth_[rad]','omega_[rad/s]','rotacc_[rad/s^2]']) 
df.to_csv('RotMotion.csv', index=False, sep=',', float_format='%10.6f')

# #Time_[s], Angle_[rad], RotationalSpeed_[rad/s], RotationalAccel_[rad/s^2]
# 0.0000   , 0.0        , 0.12                   , 0.000 
# 0.1000   , 0.2        , 0.12                   , 0.000 
# 0.2000   , 0.4        , 0.12                   , 0.000 
# 0.3000   , 0.6        , 0.12                   , 0.000 


R = 5
U0=10
tsr = omega*R/U0
print(tsr)

if __name__ == '__main__':
    pass
