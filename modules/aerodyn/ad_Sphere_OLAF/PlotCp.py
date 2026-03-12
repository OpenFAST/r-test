import os
import matplotlib.pyplot as plt
import numpy as np
from openfast_toolbox.io.vtk_file import VTKFile

# --- Read VTK file
scriptDir = os.path.dirname(__file__)
vtk = VTKFile(os.path.join(scriptDir, 'vtk_fvw/ad_driver.FVW_Glb.SrcPnl.000000002.vtk'))
print(vtk)

# --- Extract relevant coordinate along slice y=0
# We use the panel central points to identify the points on the slice y=0
# In this setup (odd number of panels), we will only get the slice that is upstream
P = vtk.cell_data['Pcent']
P[:,2] -= 5
I = np.where((P[:, 1] > -0.01) & (P[:, 1] < 0.01))[0] # Indices of the slice
x, z = P[I,0], P[I,2]
theta = np.atan2(z, -x)

# --- Extract velocity and Cp along slice
U0 = vtk.cell_data['Uwnd'][I]
V  = vtk.cell_data['Utot'][I]
Cp = vtk.cell_data['Cp'][I]
SpeedUp = np.linalg.norm(V, axis=1)/np.linalg.norm(U0, axis=1)

# Analytical values
theta_th = np.linspace(-np.pi/2,np.pi/2,100)
Cp_th      = 1/4*(9*np.cos(theta_th)**2-5)
SpeedUp_th = 3/2*np.abs(np.sin(theta_th))

# --- Plot
fig,axes = plt.subplots(1, 2, sharey=False, figsize=(12.8,4.8))
fig.subplots_adjust(left=0.07, right=0.98, top=0.94, bottom=0.11, hspace=0.20, wspace=0.20)
axes[0].plot(theta_th*180/np.pi, Cp_th,'k-', label='Theory')
axes[0].plot(theta   *180/np.pi, Cp,   '-',  label='OLAF')
axes[0].set_xlabel(r'$\theta$ [deg]')
axes[0].set_ylabel(r'$C_p$ [-]')
axes[0].legend()
axes[1].plot(theta_th*180/np.pi, SpeedUp_th,'k-', label='Theory')
axes[1].plot(theta   *180/np.pi, SpeedUp,   '-',  label='OLAF')
axes[1].set_xlabel(r'$\theta$ [deg]')
axes[1].set_ylabel(r'Speed up, $V/U_0$ [-]')
fig.suptitle('Potential flow about a 3D sphere')
fig.savefig('_Sphere_Cp.png')



plt.show()

