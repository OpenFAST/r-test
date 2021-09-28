import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# --- Rot Motion
freq1= 0.8
freq2= 0.4
tMax = 10
dt   = 0.1



omega1 = 2*np.pi*freq1
T1  = 1/freq1
omega2 = 2*np.pi*freq2
T2  = 1/freq2



time  = np.arange(0,tMax+dt/2,dt)

pos = np.zeros((len(time), 6)) # positions: x,y,z, theta_x, theta_y, theta_z
vel = np.zeros((len(time), 6)) # velocities: xdot, ydot, zdot, and omega
acc = np.zeros((len(time), 6)) # accelerations: xddot, omegadot



# -- First period we do a vertical motion
I1 = time <= T1
pos[I1,2] =           2*np.sin(omega1*time[I1]) 
vel[I1,2] = omega1   *2*np.cos(omega1*time[I1]) 
acc[I1,2] =-omega1**2*2*np.sin(omega1*time[I1]) 

# -- Second period we do nothing 
I2 = time > T1

# -- Third period we do x rotations
I3 = time > 2*T1

pos[I3,3] =            0.10 *np.sin(omega2*time[I3]) 
vel[I3,3] = omega2   * 0.10 *np.cos(omega2*time[I3]) 
acc[I3,3] =-omega2**2* 0.10 *np.sin(omega2*time[I3]) 



cols = ['time_[s]', 'x_[m]', 'y_[m]', 'z_[m]' , 'theta_x_[rad]', 'theta_y_[rad]', 'theta_z_[rad]']
cols +=['xdot_[m/s]', 'ydot_[m/s]', 'zdot_[m/s]', 'omega_x_g_[rad/s]', 'omega_y_g_[rad/s]', 'omega_z_g_[rad/s]']
cols +=['xddot_[m^2/s]', 'yddot_[m^2/s]' , 'zddot_[m^2/s]',  'alpha_x_g_[rad/s]', 'alpha_y_g_[rad/s]', 'alpha_z_g_[rad/s]']

data=np.column_stack((time, pos, vel, acc))

df = pd.DataFrame( data=data, columns=cols) 
df.to_csv('KiteMotionSimple.csv', index=False, sep=',', float_format='%10.6f')

print(df.shape)

# Time_[s] , x_[m], y_[m], z_[m] , theta_x_[rad], theta_y_[rad], theta_z_[rad-], xdot_[m/s], ydot_[m/s], zdot_[m/s], omega_x_g_[rad/s], omega_y_g_[rad/s], omega_z_g_[rad/s],  xddot_[m^2/s], yddot_[m^2/s] , zddot_[m^2/s],  alpha_x_g_[rad/s], alpha_y_g_[rad/s], alpha_z_g_[rad/s]

if __name__ == '__main__':
    pass
