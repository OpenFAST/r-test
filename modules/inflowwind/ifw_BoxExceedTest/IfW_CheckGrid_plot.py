import numpy as np
import matplotlib.pylab as plt

nzgrids=31
nygrids=31
ntgrids=4
dz=4.833333
dy=4.833333
mws=12
ref_height=90
grid_base=17.5

data = np.genfromtxt('IfW_CheckGrid.WindGrid.out', skip_header=20)

ys = np.unique(data[:,1])
zs = np.unique(data[:,2])

shape = [-1, zs.size, ys.size]

y = data[:,1].reshape(shape)[0]
z = data[:,2].reshape(shape)[0]
u = data[:,3].reshape(shape)[0]

fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

# Plot the surface.
ax.plot_surface(y, z, u, cmap='viridis', antialiased=False, rstride=1, cstride=1)
ax.set_xlabel('Y (m)')
ax.set_ylabel('Z (m)')
ax.set_zlabel('U (m/s)')

# Ymax bound
# ax.plot_surface([])

plt.show()