""" 
Convention, in body coordinates, the global "origin" is always zb=-R (tight line)


"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from numpy import cos, sin
# Local 
import welib.yams.rotations as rot
from mpl_toolkits import mplot3d

def set_axes_equal(ax):
    '''Make axes of 3D plot have equal scale so that spheres appear as spheres,
    cubes as cubes, etc..  This is one possible solution to Matplotlib's
    ax.set_aspect('equal') and ax.axis('equal') not working for 3D.

    Input
      ax: a matplotlib axis, e.g., as output from plt.gca().
    '''

    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])
    z_middle = np.mean(z_limits)

    # The plot bounding box is a sphere in the sense of the infinity
    # norm, hence I call half the max range the plot radius.
    plot_radius = 0.5*max([x_range, y_range, z_range])

    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])

def b2gl(x_b, y_b, z_b, phi_x, phi_y, phi_z):
    r_b = np.array([x_b,y_b,z_b])

    x=np.zeros(phi_x.shape)
    y=np.zeros(phi_x.shape)
    z=np.zeros(phi_x.shape)

    for i in np.ndindex(x.shape): # NOTE: j is a multi-dimension index
        A=  rot.BodyZYX_A(phi_x[i], phi_y[i], phi_z[i]); # body to global
#     for i,(px,py,pz) in enumerate(zip(phi_x, phi_y, phi_z)):
        r_gl = A.dot(r_b)
        x[i]=r_gl[0]
        y[i]=r_gl[1]
        z[i]=r_gl[2]
    #     x = z_b*(sin(phi_x)*sin(phi_z)+sin(phi_y)*cos(phi_x)*cos(phi_z)  )
    #     y = z_b*(-sin(phi_x)*cos(phi_z)+sin(phi_y)*sin(phi_z)*cos(phi_x) )
    #     z = z_b*cos(phi_x)*cos(phi_y)
    return x,y,z

def bXYZ2gl(x_b, y_b, z_b, phi_x, phi_y, phi_z):
    r_b = np.array([x_b,y_b,z_b])

    x=np.zeros(phi_x.shape)
    y=np.zeros(phi_x.shape)
    z=np.zeros(phi_x.shape)

    for i in np.ndindex(x.shape): # NOTE: j is a multi-dimension index
        A=  rot.BodyXYZ_A(phi_x[i], phi_y[i], phi_z[i]); # body to global
#     for i,(px,py,pz) in enumerate(zip(phi_x, phi_y, phi_z)):
        r_gl = A.dot(r_b)
        x[i]=r_gl[0]
        y[i]=r_gl[1]
        z[i]=r_gl[2]
    #     x = z_b*(sin(phi_x)*sin(phi_z)+sin(phi_y)*cos(phi_x)*cos(phi_z)  )
    #     y = z_b*(-sin(phi_x)*cos(phi_z)+sin(phi_y)*sin(phi_z)*cos(phi_x) )
    #     z = z_b*cos(phi_x)*cos(phi_y)
    return x,y,z


def b2eulerP(phi_x, phi_y, phi_z):
    e0 = np.zeros(phi_x.shape)
    e1 = np.zeros(phi_x.shape)
    e2 = np.zeros(phi_x.shape)
    e3 = np.zeros(phi_x.shape)
    for i in np.ndindex(phi_x.shape): # NOTE: i is a multi-dimension index
        A=  rot.BodyZYX_A(phi_x[i], phi_y[i], phi_z[i]); # body to global
        e=  rot.EulerP_fromA(A)
        e0[i]= e[0]
        e1[i]= e[1]
        e2[i]= e[2]
        e3[i]= e[3]
    return


R = 20
nRot=6.
tMax=30

t_bar=np.linspace(0,nRot*2*np.pi,100)
time = t_bar/np.max(t_bar) * tMax
dt = time[1]-time[0]


# --- Trajectory with Z,Y,X convention
azimuth   = (30*np.sin(t_bar)     )*np.pi/180   # theta_z
elevation =(90-40-10*np.sin(2*t_bar))*np.pi/180   # theta_y
heading   =  0*azimuth
# order is theta_z, theta_y, theta_x
phi_x = heading
phi_y = elevation
phi_z = azimuth

x,y,z = b2gl(0,0,R, phi_x, phi_y, phi_z)


# --- Get trajectory
# phi_x = (30*np.sin(t_bar)     )*np.pi/180  
# phi_y = (90-40-10*np.sin(-2*t_bar))*np.pi/180  
# phi_z =phi_y*0
phi_x = (30*np.sin(t_bar)     )*np.pi/180  
phi_y = (90-40-10*np.sin(-2*t_bar))*np.pi/180  
phi_z =phi_y*0
x2,y2,z2 = bXYZ2gl(0,0,R, phi_x, phi_y, phi_z)

# --- figure out direction of motion, and point x opposite to it
dx=np.diff(x2)
dy=np.diff(y2)
dz=np.diff(z2)

ex=np.zeros((3,len(x2)))
ey=np.zeros((3,len(x2)))
ez=np.zeros((3,len(x2)))

for i in np.arange(0,len(phi_x)-1):
    A = rot.BodyXYZ_A(phi_x[i], phi_y[i], 0); # body to global
    e_m_gl =-np.array([dx[i], dy[i], dz[i]])  # opposite to direction of motion
    e_m_b  = (A.T).dot(e_m_gl) # motion in body coordinates
    phi_z[i] = np.arctan2(e_m_b[1],e_m_b[0])

    A = rot.BodyXYZ_A(phi_x[i], phi_y[i], phi_z[i]); # body to global
    ex[:,i] = A[:,0]
    ey[:,i] = A[:,1]
    ez[:,i] = A[:,2]

phi_z[-1] = phi_z[-2]


# ---- Compute kinematics
pos = np.zeros((len(time), 6)) # positions: x,y,z, theta_x, theta_y, theta_z
vel = np.zeros((len(time), 6)) # velocities: xdot, ydot, zdot, and omega
acc = np.zeros((len(time), 6)) # accelerations: xddot, omegadot

phi_x_dot = np.diff(phi_x)/dt
phi_y_dot = np.diff(phi_y)/dt
phi_z_dot = np.diff(phi_z)/dt

phi_x_dot = np.concatenate(([phi_x_dot[0]], phi_x_dot))
phi_y_dot = np.concatenate(([phi_y_dot[0]], phi_y_dot))
phi_z_dot = np.concatenate(([phi_z_dot[0]], phi_z_dot))

phi_x_ddot = np.concatenate( ([0], np.diff(phi_x_dot)/dt ))
phi_y_ddot = np.concatenate( ([0], np.diff(phi_y_dot)/dt ))
phi_z_ddot = np.concatenate( ([0], np.diff(phi_z_dot)/dt ))

pos[:,3] = phi_x
pos[:,4] = phi_y
pos[:,5] = phi_z

for i in np.arange(0,len(phi_x)-1):
    G = rot.BodyXYZ_G(phi_x[i], phi_y[i], phi_z[i]); # omega_global = G theta_dot
    omega_gl = G.dot(np.array([phi_x_dot[i], phi_y_dot[i], phi_z_dot[i]]))
    alpha_gl = G.dot(np.array([phi_x_ddot[i], phi_y_ddot[i], phi_z_ddot[i]]))

    vel[i,3] = omega_gl[0]
    vel[i,4] = omega_gl[1]
    vel[i,5] = omega_gl[2]

    acc[i,3] = alpha_gl[0]
    acc[i,4] = alpha_gl[1]
    acc[i,5] = alpha_gl[2]



RR=np.sqrt(x2**2+y2**2+z2**2)
print(np.unique(RR))

# Convert to Euler parameters
e = b2eulerP(phi_x, phi_y, phi_z)


phi_y_sp = np.linspace(0,np.pi/2,11) # [0,pi]
phi_z_sp = np.linspace(-np.pi/2,np.pi/2,11) # [0,2pi]
PHI_Y_SP, PHI_Z_SP = np.meshgrid(phi_y_sp, phi_z_sp)
PHI_X_SP= 0*PHI_Y_SP
x_sp, y_sp, z_sp = b2gl(0,0,R, PHI_X_SP, PHI_Y_SP, PHI_Z_SP)

x_gr, y_gr = np.meshgrid([0, R], [-R,R])



fig = plt.figure()
ax = plt.axes(projection='3d')
# ax.plot(x,y,z    , label='')
ax.plot(x2,y2,z2    , label='')

I=np.linspace(0,len(t_bar)-2,7).astype(int)
print(I)
for i in I:
    ax.plot([x2[i], x2[i]+ex[0,i]],[y2[i], y2[i]+ex[1,i]],[z2[i], z2[i]+ex[2,i]], 'r-'   )
    ax.plot([x2[i], x2[i]+ey[0,i]],[y2[i], y2[i]+ey[1,i]],[z2[i], z2[i]+ey[2,i]], 'g-'   )
    ax.plot([x2[i], x2[i]+ez[0,i]],[y2[i], y2[i]+ez[1,i]],[z2[i], z2[i]+ez[2,i]], 'b-'   )

    ax.plot([0, x2[i]],[0, y2[i]],[0, z2[i]], 'k-'   )

ax.plot(x_sp.ravel(),y_sp.ravel(),z_sp.ravel()    , 'k.',label='')
ax.plot_surface(x_gr, y_gr, 0*x_gr)

ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
ax.legend()
set_axes_equal(ax)
plt.show()


# ---

cols = ['time_[s]', 'x_[m]', 'y_[m]', 'z_[m]' , 'theta_x_[rad]', 'theta_y_[rad]', 'theta_z_[rad]']
cols +=['xdot_[m/s]', 'ydot_[m/s]', 'zdot_[m/s]', 'omega_x_g_[rad/s]', 'omega_y_g_[rad/s]', 'omega_z_g_[rad/s]']
cols +=['xddot_[m^2/s]', 'yddot_[m^2/s]' , 'zddot_[m^2/s]',  'alpha_x_g_[rad/s]', 'alpha_y_g_[rad/s]', 'alpha_z_g_[rad/s]']

data=np.column_stack((time, pos, vel, acc))

df = pd.DataFrame( data=data, columns=cols) 
df.to_csv('KiteMotion8.csv', index=False, sep=',', float_format='%10.6f')



print('pos 0', pos[0,0:3], pos[0,3:6]*180/np.pi)
