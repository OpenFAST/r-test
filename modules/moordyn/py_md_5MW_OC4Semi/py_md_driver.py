#*******************************************************************************
# LICENSING
# Copyright (C) 2021 National Renewable Energy Laboratory
# Author: Nicole Mendoza
#
# This file is part of MoorDyn.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#*******************************************************************************
#
# This is an exampe of Python driver code for MoorDyn 
#
# Usage: This program gives an example for how the user calls the main
#        subroutines of MoorDyn, and thus is specific to the user
#
# Basic alogrithm for using MoorDyn python library
#   1.  initialize python wrapper library
#           set necessary library values
#           set input file string arrays (from file or script)
#   2.  initialize MoorDyn Fortran library
#           set initial position, velocity, acceleration values
#           call moordyn_init once to initialize
#           Handle any resulting errors
#   3.  timestep iteration
#           set extrapolated values for inputs
#           call moordyn_updatestates to propogate forwared from t to t+dt
#           set position, velocity, and acceleration information for all nodes
#           call moordyn_calcoutput.  Handle any resulting errors
#           return the resulting force and moment array
#           aggregate output channnels
#   4. End
#         call moordyn_end to close the MoorDyn library and free memory
#         handle any resulting errors
#
#
import numpy as np   
import os
import sys

# path to find the moordyn_library.py from the local directory
sys.path.insert(0, os.path.sep.join(["..", "..", "..", "..", "..", "modules", "moordyn", "python-lib"]))
import moordyn_library      # this file handles the conversion from python to c-bound types and should not be changed by the user

###############################################################################
# Locations to build directory relative to r-test directory.  This is specific
# to the regession testing with openfast and will need to be updated when
# coupled to other codes or use cases

basename = "libmoordyn_c_binding"
if sys.platform == "linux" or sys.platform == "linux2":
    library_path = os.path.sep.join(["..", "..", "..", "..", "..", "build", "modules", "moordyn", basename + ".so"])
elif sys.platform == "darwin":
    library_path = os.path.sep.join(["..", "..", "..", "..", "..", "build", "modules", "moordyn", basename + ".dylib"])
elif sys.platform == "win32":
    # Windows may have this library installed in one of two locations depending
    # on which build system was used (CMake or VS).
    library_path = os.path.sep.join(["..", "..", "..", "..", "..", "build", "modules", "moordyn", basename + ".dll"])   # cmake install location
    if not os.path.isfile(library_path) and not sys.maxsize > 2**32:        # Try VS build location otherwise
        library_path = os.path.sep.join(["..", "..", "..", "..", "..", "build", "bin", "MoorDyn_c_binding_Win32.dll"]) # VS build install location
        if not os.path.isfile(library_path):
            print(f"Python is 32 bit and cannot find 32 bit MoorDyn_c_binding DLL expected at: {library_path}")
            exit(1)
    if not os.path.isfile(library_path) and sys.maxsize > 2**32:        # Try VS build location otherwise
        library_path = os.path.sep.join(["..", "..", "..", "..", "..", "build", "bin", "MoorDyn_c_binding_x64.dll"]) # VS build install location
        if not os.path.isfile(library_path):
            print(f"Python is 64 bit and cannot find 64 bit MoorDyn_c_binding DLL expected at: {library_path}")
            exit(1)

# Library path
try: 
    # User inserts their own appropriate library path here
    md_lib = moordyn_library.MoorDynLib(library_path)
except Exception as e:
    print("{}".format(e))
    print(f"MD: Cannot load MoorDyn library at {library_path}")
    exit(1)



# MD Main input file
# Can either use this or the input-file-contents-as-string-array - ONE OR THE OTHER, NOT BOTH!
md_input_file = "md_primary.inp"

# Saving outputs
#       When coupled to another code, the channels requested in the outlist
#       section of the output file are passed back for writing to file.  Here
#       we will write the aggregated output channels to a file at the end of
#       the simulation.
md_output_file = "MD.out"

# For debugging only
verbose = False # User can set this to false for routine operations
if verbose:
    dbgFileName = "MD.dbg"
    dbg_outfile = moordyn_library.DriverDbg(dbgFileName)

# Test file
# Note this only contains channels for platform motions
#       B1Surge B1Sway B1Heave B1Roll B1Pitch B1Yaw 
#       B1TVxi B1TVyi B1TVzi B1RVxi B1RVyi B1RVzi
#       B1TAxi B1TAyi B1TAzi B1RAxi B1RAyi B1RAzi)
md_test_file = "5MW_OC4Semi_WSt_WavesWN.out"

#=============================================================================================================================
#-------------------------------------------------------- SET INPUTS ---------------------------------------------------------
#=============================================================================================================================

# Main input file - MoorDyn V2
# Usage: the contents of this string follow the identical syntax to what is described for the MoorDyn input file in the user guides and documentation
# Please modify the string contents based on your specific use case
md_input_string_array = []

#   Main MoorDyn input file
#       This file is read from disk to an array of strings with the line
#       endings stripped off.  This array will have the same number of elements
#       as there are lines in the file.
# The input file will only be loaded once
try:
    fh = open(md_input_file, "r")
except Exception as e:
    print("{}".format(e))
    print(f"Cannot load MoorDyn input file")
    exit(1)

for line in fh:
  # strip line ending and ending white space and add to array of strings
  md_input_string_array.append(line.rstrip())
fh.close()

# Test file for MoorDyn time-accurate inputs from OC4 Semi Test Case
try:
    ft = open(md_test_file, "r")
    tmp = ft.read().splitlines() # each line in file is a row in tmp
    tmp2 = tmp[8:-1] # skip the header rows - get the raw data only
    data = np.empty([len(tmp2),96])
    time = np.empty(len(tmp2))
    for d in range(0,len(tmp2)):
        tmp3 = tmp2[d].split() # split the row into columns
        for k in range(0,len(tmp3)):
            data[d,k] = float(tmp3[k]) # for each column, convert the string into a float
        time[d] = data[d,0]
    ft.close()
except Exception as e:
    print("{}".format(e))
    print(f"Cannot load MoorDyn test file")
    exit(1)


#==============================================================================
# Basic alogrithm for using the MoorDyn library

# Time inputs
t_start             = time[0]            # initial or start time. MUST BE >= 0
md_lib.dt           = time[1] - time[0]  # time interval
md_lib.total_time   = time[-1]           # total or end time
# time                = np.arange(t_start,md_lib.total_time + md_lib.dt,md_lib.dt)
md_lib.numTimeSteps = len(time)

# System inputs
g                   = 9.80665            # gravitational acceleration (m/s^2). usage: g is positive
rho_h2o             = 1025               # water density (kg/m^3)
d_h2o               = 200                # water depth (m). usage: depth is positive
platform_init_pos   = np.array([data[0, 1], data[0, 2], data[0, 3], data[0, 4], data[0, 5], data[0, 6]]) # platform/hull/substructure initial position [x, y, z, Rx, Ry, Rz] in openFAST global coordinates [m, m, m, rad, rad, rad]
platform_init_vel   = np.array([data[0, 7], data[0, 8], data[0, 9], data[0,10], data[0,11], data[0,12]]) # platform/hull/substructure initial velocities [x,y,z,Rx,Ry,Rz]_dot  -- first deriv (velocities)
platform_init_acc   = np.array([data[0,13], data[0,14], data[0,15], data[0,16], data[0,17], data[0,18]]) # platform/hull/substructure initial accelerations [x,y,z,Rx,Ry,Rz]_ddot -- second deriv (accelerations)
forces              = np.array([data[0,0], data[0,0], data[0,0], data[0,0], data[0,0], data[0,0]]) # platform/hull/substructure forces (output) [Fx,Fy,Fz,Mx,My,Mz]   -- resultant forces/moments at each node

# Interpolation Order - MUST BE 1: linear (uses two time steps) or 2: quadratic (uses three time steps)
InterpOrder         = 2

# PREDICTOR-CORRECTOR: For checking if our library is correctly handling correction steps, set this to > 0
NumCorrections      = 0 # SET TO 0 IF NOT DOING CORRECTION STEP

#=============================================================================================================================
#-------------------------------------------------------- RUN MOORDYN --------------------------------------------------------
#=============================================================================================================================

# MD_INIT: Only need to call md_init once
# ----------------------------------------------------------------------------------------------------------------------------
try:
    md_lib.md_init(md_input_string_array, g, rho_h2o, d_h2o, platform_init_pos, InterpOrder)
except Exception as e:
    print("{}".format(e))   # Exceptions handled in moordyn_library.py
    if verbose:
        #dbg_outfile.write("MD driver: MD init call failed")
        dbg_outfile.end()
    exit(1)

# Set up the output channels listed in the MD input file
output_channel_names = md_lib._channel_names.value
output_channel_units = md_lib._channel_units.value
output_channel_values = np.zeros(md_lib._numChannels.value)
output_channel_array  = np.zeros( (md_lib.numTimeSteps,md_lib._numChannels.value+1) ) # includes time

# MD_calcOutput: calculates outputs for initial time t=0 and initial position & velocity
# ----------------------------------------------------------------------------------------------------------------------------
try: 
    md_lib.md_calcOutput(time[0], platform_init_pos, platform_init_vel, platform_init_acc, forces, output_channel_values)
except Exception as e:
    print("{}".format(e))   # Exceptions handled in moordyn_library.py
    if verbose:
        #dbg_outfile.write("MD driver: MD initial calcOutput call failed")
        dbg_outfile.end()
    exit(1)

# Write the outputs at t = t_initial
output_channel_array[0,:] = np.append(time[0],output_channel_values)
if verbose:
    dbg_outfile.write(time[0],platform_init_pos,platform_init_vel,platform_init_acc,forces)

# Run MD at each time step
# ----------------------------------------------------------------------------------------------------------------------------
for i in range( 0, len(time)-1):

    # Current t = time[i]

    # print time every simulation second
    if (i % round(1.0/md_lib.dt))==0:
        print(f"Time: {time[i]}")

    # IF DOING PREDICTOR-CORRECTOR
    for correction in range(0, NumCorrections+1):

        # User must update position, velocities, and accelerations at each time step
        # Note: MD currently handles one interface point, i.e. substructure is represented as a single point
        Positions     = [data[i, 1], data[i, 2], data[i, 3], data[i, 4], data[i, 5], data[i, 6]]
        Velocities    = [data[i, 7], data[i, 8], data[i, 9], data[i,10], data[i,11], data[i,12]]
        Accelerations = [data[i,13], data[i,14], data[i,15], data[i,16], data[i,17], data[i,18]]

        # Call md_updateStates - propagate the arrays
        try: 
            md_lib.md_updateStates(time[i], time[i+1], Positions, Velocities, Accelerations) # positions, velocities, and accelerations are all at current time
        except Exception as e:
            print("{}".format(e))   # Exceptions handled in moordyn_library.py
            if verbose:
                #dbg_outfile.write("MoorDyn_Driver.py: MD_updateStates call failed")
                dbg_outfile.end()
            exit(1)

        # Call md_calcOutput: calculate outputs for the current time step @ t+dt
        try: 
            md_lib.md_calcOutput(time[i+1], Positions, Velocities, Accelerations, forces, output_channel_values) # output channel values are overwritten for each time step
        except Exception as e:
            print("{}".format(e))   # Exceptions handled in moordyn_library.py
            if verbose:
                #dbg_outfile.write("MoorDyn_Driver.py: MD_calcOutput call failed")
                dbg_outfile.end()
            exit(1)
        
        # Clean up before moving on to next time step
        output_channel_array[i+1,:] = np.append(time[i+1],output_channel_values)
        if verbose:
            dbg_outfile.write(time[i+1],Positions,Velocities,Accelerations,forces)

# MD_END: Only need to call md_end once when you're done
# ----------------------------------------------------------------------------------------------------------------------------
try:
    md_lib.md_end()
except Exception as e:
    print("{}".format(e))   # Exceptions handled in moordyn_library.py
    if verbose:
        #dbg_outfile.write("MoorDyn_Driver.py: MD_end call failed")
        dbg_outfile.end()
    exit(1)

# Finally, write the ouput channel values to a file
OutFile=moordyn_library.WriteOutChans(md_output_file,md_lib.output_channel_names,md_lib.output_channel_units)
OutFile.write(output_channel_array)
OutFile.end()
exit()
