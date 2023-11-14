"""
Standalone script to read an ASCII OpenFAST output and plot some channels.

Contact: E. Branlard 
"""
import os
import numpy as np
import matplotlib.pyplot as plt

# --- Parameters
outfile      = 'Main.out'
plotChannels = ['OoPDefl1','IPDefl1','TTDspFA','TTDspSS']

# --- Read out file
# NOTE: it's best to use FASTOutputFile from the python-toolbox instead:
#    from pyFAST.input_output.fast_output_file import FASTOutputFile
#    df = FASTOutputFile(outfile).toDataFrame()
with open(outfile) as fid:
    headers = [fid.readline() for _ in range(6)] # Read header
    channels = fid.readline().strip().split()    # Channel names
    units = fid.readline().strip().split()       # Channel units
data = np.loadtxt(outfile, skiprows=8)           # time series
print('Available channels:', channels)

# --- Plot list of selected channels
nPlots = len(plotChannels)
time = data[:,0]

fig,axes = plt.subplots(nPlots, 1, sharex=True, figsize=(6.4,8))
fig.subplots_adjust(left=0.12, right=0.95, top=0.98, bottom=0.05, hspace=0.20, wspace=0.20)

for ip, (ax, chan) in enumerate(zip(axes, plotChannels)):
    # Find index of plot channel within data
    id = channels.index(chan)
    ax.plot(time, data[:,id])
    ax.set_xlabel('Time (s)')
    ax.set_ylabel(channels[id] + ' ' + units[id])
    ax.grid()
fig.savefig(os.path.dirname(__file__)+'.png')
plt.show()

