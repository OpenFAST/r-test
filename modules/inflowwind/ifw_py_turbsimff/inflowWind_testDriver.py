#**********************************************************************************************************************************
# LICENSING
# Copyright (C) 2021 National Renewable Energy Lab
#
# This file is a test case for the InflowWind C-bindings library with python 
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
#**********************************************************************************************************************************
#
# This is the Python driver code for InflowWind
# Usage: This program gives an example for how the user calls the main subroutines of inflowWind, and thus is specific to the user
import numpy as np
import os
import datetime
import sys
sys.path.insert(0, os.path.sep.join(["..", "..", "..", "..", "..", "modules", "inflowwind", "python-lib"]))
import inflowwind_library # this file handles the conversion from python to c-bound types and should not be changed by the user

# Files for testing IO
primaryFile="ifw_primary.inp"           # primary IfW input file to read and pass
uniformFile="UniformWindInput.inp"      # Uniform wind input file to read
positionFile="Points.inp"               # Nx3 position info
velocityFile="Points.Velocity.dat"      # Resulting output file


# Locations to build directory relative to r-test directory
if sys.platform == "linux" or sys.platform == "linux2":
    library_path = os.path.sep.join(["..", "..", "..", "..", "..", "install", "lib", "libifw_c_lib.so"])
elif sys.platform == "darwin":
    library_path = os.path.sep.join(["..", "..", "..", "..", "..", "install", "lib", "libifw_c_lib.dylib"])
elif sys.platform == "win32":
    library_path = os.path.sep.join(["..", "..", "..", "..", "..", "install", "lib", "libifw_c_lib.dll"])   # cmake install location 
    if not os.path.isfile(library_path):        # Try VS build location otherwise
        library_path = os.path.sep.join(["..", "..", "..", "..", "..", "build", "bin", "libifw_c_lib.dll"]) # VS build install location

#=============================================================================================================================
#------------------------------------------------------- INPUT FILES ---------------------------------------------------------
#=============================================================================================================================

# Main inflowWind input file
# Usage: the contents of this string follow the identical syntax to what is described for the inflowWind input file in the user guides and documentation
# Please modify the string contents based on your specific use case
ifw_input_string_array = []
fh = open(primaryFile, "r")
for line in fh:
  ifw_input_string_array.append(line.rstrip())
fh.close()


#----------------------------------------------------------------------------------------------------------------------------------

# Uniform wind input file - only needed for WindType = 2
# Usage: Please modify the string contents based on your specific use case. Syntax follows user guides and documentation. Must have as input.
ifw_uniform_string_array=[]
fh = open(uniformFile, "r")
for line in fh:
  ifw_uniform_string_array.append(line.rstrip())
fh.close()


#=============================================================================================================================
#----------------------------------------------------- FUNCTION CALLS --------------------------------------------------------
#=============================================================================================================================

try:
    ifwlib = inflowwind_library.InflowWindLibAPI(library_path)
except:
    print(f"Cannot load library at {library_path}")
    exit(1)


# Time inputs - user adjusts as needed/desired  -- set to match values in the  modules/inflowwind fortran regression test
t_start             = 30                 # initial time
ifwlib.dt           = 0.1                # time interval that it's being called at, not usedby IFW, only here for consistency with other modules
ifwlib.total_time   = 30.8               # final or total time
time                = np.arange(t_start,ifwlib.total_time + ifwlib.dt,ifwlib.dt) # total time + increment because python doesnt include endpoint!
ifwlib.numTimeSteps = len(time)

# Initialize arrays
# User shall update the positions array for each time step for their application. 
# Coordinates are N x 3 ([x, y, z]) in the openfast global coordinate system (aka inertial coordinates). 
positions=[]
fh=open(positionFile, "r")
for line in fh:
    if not line.startswith('#'):
        positions.append([float(i) for i in line.split()])
positions = np.asarray(positions)
fh.close()

# check that we read in a Nx3
if positions.shape[1] != 3:
    print("Error in parsing the points file.  Does not contain a Nx3 set of position points")
    exit(1)

ifwlib.numWindPts   = positions.shape[0]              # total number of wind points requesting velocities for at each time step. must be integer
velocities          = np.zeros((ifwlib.numWindPts,3)) # output velocities (N x 3) - also in openfast global coordinate system

# SUBROUTINE CALLS ========================================================================================================

# NOTE: the error handling here is handled locally since this is the only
#       driver code.  If InflowWind is incorporated into another code, the
#       error handling will need to be passed to the main code.  That way the
#       main code can close other modules as necessary (otherwise you will end
#       up with memory leaks and a bunch of garbage in the other library
#       instances).

# IFW_INIT: Only need to call ifw_init once
try:
    ifwlib.ifw_init(ifw_input_string_array, ifw_uniform_string_array)
except Exception as e:
    print("{}".format(e))
    exit(1)

outputChannelValues = np.zeros(ifwlib._numChannels.value)


# open output file
try:
    OutFile=open(velocityFile,'wt')
except:
    print(f"Could not open results file {velocityFile} for writing")
    exit(1)

# write file head
t_string=datetime.datetime.now()
dt_string=datetime.date.today()
#.strftime("%b-%d-%Y at %H:%M:%S")
n = OutFile.write(f"## This file was generated by InflowWind_Driver on {dt_string.strftime('%b-%d-%Y')} at {t_string.strftime('%H:%M:%S')}\n")
n = OutFile.write(f"## This file contains the wind velocity at the {ifwlib.numWindPts} points specified in the file ")
n = OutFile.write(f"{positionFile}\n")
n = OutFile.write("#\n")
n = OutFile.write("#        T                X                Y                Z                U                V                W\n")
n = OutFile.write("#       (s)              (m)              (m)              (m)             (m/s)            (m/s)            (m/s)\n")


# IFW_CALCOUTPUT: Loop over ifw_calcOutput as many times as needed/desired by user
idx = 0
for t in time:

    # When coupled to another code, set the positions info for this timestep
    # here.

    try:
        ifwlib.ifw_calcOutput(t, positions, velocities, outputChannelValues)
    except Exception as e:
        print("{}".format(e))
        OutFile.close()
        exit(1)
    
    # write the Velocity data out -- this is used in comparisons for validation of the python interface
    for p, v in zip(positions,velocities):
        n = OutFile.write('  %14.7f   %14.7f   %14.7f   %14.7f   %14.7f   %14.7f   %14.7f\n' % (t,p[0],p[1],p[2],v[0],v[1],v[2]))

    # When coupled to a different code, this is where the velocity info would
    # be passed to other things.


    # Store the channel outputs -- these are requested from within the IfW input
    # file OutList section
    ifwlib._channel_output_array = outputChannelValues
    ifwlib._channel_output_values[idx,:] = ifwlib._channel_output_array

    # Step to next timestep
    idx = idx + 1


OutFile.close()


# IFW_END: Only need to call ifw_end once.
#   NOTE:   in the event of an error during the above Init or CalcOutput calls,
#           the IfW_End routine will be called during that error handling.
#           This works for IfW, but may not be a desirable way to handle
#           errors in other codes (we may still want to retrieve some info
#           from memory before clearing out everything).
#   NOTE:   Error handling from the ifw_end call may not be entirely necessary,
#           but we may want to know if some memory was not released properly or
#           a file not closed correctly.
try:
    ifwlib.ifw_end()
except Exception as e:
    print("{}".format(e))
    exit(1)



print("InflowWind completed.")
exit(0)

