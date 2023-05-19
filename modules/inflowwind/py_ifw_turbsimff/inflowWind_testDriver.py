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
# This is an example of Python driver code for InflowWind
#
# Usage: This program gives an example for how the user calls the main
#        subroutines of inflowWind, and thus is specific to the user
#
# Basic alogrithm for using InflowWind python library
#   1.  initialize python wrapper library
#           set necessary library values
#               numWindPts
#               dt
#               numTimeSteps
#           set input file string arrays (from file or script)
#   2.  initialize InflowWind Fortran library
#           call ifw_init once to initialize IfW
#           Handle any resulting errors
#   3.  timestep iteration
#           set array of positions to pass
#           call ifw_calcoutput.  Handle any resulting errors
#           return the resulting velocities array
#           aggregate output channnels
#   4. End
#         call ifw_end to close the InflowWind library and free memory
#         handle any resulting errors
#
#
import numpy as np
import os
import sys

# path to find the inflowwind_library.py from the local directory
os.chdir(sys.path[0])
ifwLibPath=os.path.sep.join(["..", "..", "..", "..", "..", "modules", "inflowwind", "python-lib"])
sys.path.insert(0, ifwLibPath)
print(f"Importing 'inflowwind_library' from {ifwLibPath}")
import inflowwind_library # this file handles the conversion from python to c-bound types and should not be changed by the user

###############################################################################
# Locations to build directory relative to r-test directory.  This is specific
# to the regession testing with openfast and will need to be updated when
# coupled to other codes or use cases

basename = "libifw_c_binding"
if sys.platform == "linux" or sys.platform == "linux2":
    library_path = os.path.sep.join(["..", "..", "..", "..", "..", "build", "modules", "inflowwind", basename + ".so"])
elif sys.platform == "darwin":
    library_path = os.path.sep.join(["..", "..", "..", "..", "..", "build", "modules", "inflowwind", basename + ".dylib"])
elif sys.platform == "win32":
    # Windows may have this library installed in one of two locations depending
    # on which build system was used (CMake or VS).
    library_path = os.path.sep.join(["..", "..", "..", "..", "..", "build", "modules", "inflowwind", basename + ".dll"])   # cmake install location
    if not os.path.isfile(library_path) and not sys.maxsize > 2**32:        # Try VS build location otherwise
        library_path = os.path.sep.join(["..", "..", "..", "..", "..", "build", "bin", "InflowWind_c_binding_Win32.dll"]) # VS build install location
        if not os.path.isfile(library_path):
            print(f"Python is 32 bit and cannot find 32 bit InflowWind DLL expected at: {library_path}")
            exit(1)
    if not os.path.isfile(library_path) and sys.maxsize > 2**32:        # Try VS build location otherwise
        library_path = os.path.sep.join(["..", "..", "..", "..", "..", "build", "bin", "InflowWind_c_binding_x64.dll"]) # VS build install location
        if not os.path.isfile(library_path):
            print(f"Python is 64 bit and cannot find 64 bit InflowWind DLL expected at: {library_path}")
            exit(1)



###############################################################################
# For testing, a set of input files is read in.  Everything in these input
# files could in principle be hard coded into this script.  These are separated
# out for convenience in testing.

#   Primary input
#       This is identical to what InflowWind would read from disk if we were
#       not passing it.  When coupled to other codes, this may be passed
#       directly from memory (i.e. during optimization with WEIS), or read as a
#       template and edited in memory for each iteration loop.
primary_file="ifw_primary.inp"

#   Uniform wind input file
#       This is identical to what InflowWind would read from disk if we were
#       not passing it through the interface.  When coupled to other codes,
#       this may be passed directly from memory (i.e. during optimization with
#       WEIS), or potentially not even used if turbulent wind inputs are used
#       instead (which would need to be read from disk).
uniform_file="UniformWindInput.inp"

#   Positions array
#       When coupled to another code, an array of positions (N points of
#       [X,Y,Z] values) would be passed from the structural code.  Since this
#       driver is standalone, we will read in an array of points that will be
#       passed through to InflowWind at each timestep.  This is read in from
#       disk once at the start of this code into the positions array.  When
#       coupled to other codes, this file would not exist.
position_file="Points.inp"

#   Velocities array output file
#       When coupled into another code, an array of velocities would be
#       returned corresponding to the positions array passed in.  For testing
#       purposes, we will write these values to disk.  When coupled to other
#       codes, this file would not exist.
velocities_file="Points.Velocity.dat"

#   Output file
#       When coupled to another code, the channels requested in the outlist
#       section of the output file are passed back for writing to file.  Here
#       we will write the aggregated output channels to a file at the end of
#       the simulation.
output_file="ifw_primary.out"


#------------------------------------------------------- INPUT FILES ---------------------------------------------------------
#=============================================================================================================================

#   Main inflowWind input file
#       For testing, we read in the file from disk and store it in an array of
#       strings with the line endings stripped off.  This array will be have
#       the same number of elements as there are lines in the file.
ifw_input_string_array = []     # instantiate empty array
fh = open(primary_file, "r")
for line in fh:
  # strip line ending and ending white space and add to array of strings
  ifw_input_string_array.append(line.rstrip())
fh.close()

#   Uniform wind input file - only needed for WindType = 2
#       Also for testing, we read this file in from disk before the simulation.
ifw_uniform_string_array=[]
fh = open(uniform_file, "r")
for line in fh:
  ifw_uniform_string_array.append(line.rstrip())
fh.close()


#=============================================================================================================================
#----------------------------------------------------- FUNCTION CALLS --------------------------------------------------------
#=============================================================================================================================

#   Instantiate the ifwlib python object
#       wrap this in error handling in case the library_path is incorrect
try:
    ifwlib = inflowwind_library.InflowWindLib(library_path)
except Exception as e:
    # Do any clean up and final output
    print("{}".format(e))
    print(f"Cannot load library at {library_path}")
    exit(1)

#   Time inputs
#       For this test case, we are checking between 30 and 30.8 seconds.  The
#       inflowwind python library interface must be informed about the
#       following 2 time related information variables
#           ifwlib.dt           -- the timestep inflowwind is called at.
#           ifwlib.numTimeSteps -- total number of timesteps, only used to
#                                  construct arrays to hold the output channel
#                                  info
t_start             = 30                 # initial time
ifwlib.dt           = 0.1                # time interval that it's being called at, not usedby IFW, only here for consistency with other modules
final_time          = 30.8               # final time
time                = np.linspace(t_start, final_time, 9) # total time + increment because python doesnt include endpoint!
ifwlib.numTimeSteps = len(time)          # only for constructing array of output channels for duration of simulation

#   Initialize position array 
#       For testing, a set of points is read from the position_file and stored
#       as a N x 3 ([x, y, z]).  These coordinates are in the openfast global
#       coordinate system (aka inertial coordinates).  In this test case, these
#       values are read in once at the begining, and held constant at each
#       timestep call.  These could be hard coded as a smaller set of points
#       for testing, but this test is designed to match an equivalent fortran
#       driver test as a way to verify that the coupling from python through
#       fortran and back is correct.
#
#           positions = np.array([  # position array originally used in develop
#               [0.0,  0.0, 150],
#               [0.0,  0.0, 125],
#               [0.0,  0.0, 175],
#               [0.0,  25., 150],
#               [0.0, -25., 150],
#               [0.0,  25., 175],
#               [0.0, -25., 175],
#               [0.0,  25., 125],
#               [0.0, -25., 125]
#           ])
#
#       When coupled to a different code, this array would be passed from the
#       structural solver with the X,Y,Z points for location the wind velocity
#       is needed (i.e. nodes on a rotor).  As the simulation progresses, these
#       positions would change.  However, the number of points that wind data
#       is requested for must be the same throughout the simulation (in other
#       words, don't change the size of this array between calls to IfW).
positions=[]
fh=open(position_file, "r")
for line in fh:
    if not line.startswith('#'):
        positions.append([float(i) for i in line.split()])
positions = np.asarray(positions)
fh.close()

#  Check that the array is of the correct shape
if positions.shape[1] != 3:
    raise ValueError("Error in parsing the points file. Does not contain a Nx3 set of position points")

#  numWindPts
ifwlib.numWindPts   = positions.shape[0]              # total number of wind points requesting velocities for at each time step. must be integer

#  Matching velocities array for the velocities reported from IfW
velocities          = np.zeros((ifwlib.numWindPts,3)) # output velocities (N x 3) - also in openfast global coordinate system


#==============================================================================
# Basic alogrithm for using InflowWind library
#
# NOTE: the error handling here is handled locally since this is the only
#       driver code.  If InflowWind is incorporated into another code, the
#       error handling will need to be passed to the calling-code so that
#       it can close other modules as necessary (otherwise you will end
#       up with memory leaks and a bunch of garbage in the other library
#       instances).

# IFW_INIT: Only need to call ifw_init once
try:
    ifwlib.ifw_init(ifw_input_string_array, ifw_uniform_string_array)
except Exception as e:
    # Do any required clean up
    print("{}".format(e))   # Exception is from inflowwind_library.py
    exit(1)


#  To get the names and units of the output channels
#output_channel_names = ifwlib.output_channel_names
#output_channel_units = ifwlib.output_channel_units


#  Set the array holding the ouput channel values to zeros initially.  Output
#  channel values returned from each CalcOutput call in this array.  We will
#  aggregate them together in the time stepping loop to get the entire time
#  series.  Time channel is not included, so we must add that.
outputChannelValues = np.zeros(ifwlib.numChannels)
allOutputChannelValues = np.zeros( (ifwlib.numTimeSteps,ifwlib.numChannels+1) )


#   Open debug output file for regession testing purposes.
DbgOutfile = inflowwind_library.DebugOut(velocities_file,ifwlib.numWindPts)


#   Timestep iteration
#       Step through all the timesteps.
#           1.  set the positions array with node positions from the structural
#               solver
#           2.  call Ifw_CalcOutput_C to retreive the corresponding velocities
#               to pass back to the calling code (or write to disk in this
#               example).
#
for i, t in enumerate(time):

    #   When coupled to another code, set the positions info for this timestep
    #   here in the calling algorithm.  For this regression test example, the
    #   positions are kept constant throughout the simulation.

    try:
        ifwlib.ifw_calc_output(t, positions, velocities, outputChannelValues)
    except Exception as e:
        print("{}".format(e))
        DbgOutfile.end()
        exit(1)
    

    #   When coupled to a different code, this is where the velocity info would
    #   be passed to the aerodynamic solver.
    #
    #   For this regression test example, we will write this to file (in
    #   principle this could be aggregated and written out once at the end of
    #   the regression simulation, but for simplicity we are writting one line
    #   at a time during the call).  The regression test will have one row for
    #   each timestep + position array entry.
    DbgOutfile.write(t, positions, velocities)


    # Store the channel outputs -- these are requested from within the IfW input
    # file OutList section.  In OpenFAST, these are added to the output
    # channel array for all modules and written to that output file.  For this
    # example we will write to file at the end of the simulation in a single
    # shot.
    allOutputChannelValues[i,:] = np.append(t, outputChannelValues)


DbgOutfile.end()   # close the regression test example output file


# IFW_END: Only need to call ifw_end once.
#   NOTE:   in the event of an error during the above Init or CalcOutput calls,
#           the IfW_End routine will be called during that error handling.
#           This works for IfW, but may not be a desirable way to handle
#           errors in other codes (we may still want to retrieve some info
#           from memory before clearing out everything).
#   NOTE:   Error handling from the ifw_end call may not be entirely necessary,
#           but we may want to know if some memory was not released properly or
#           a file not closed correctly.
ifwlib.ifw_end()


#   Now write the ouput channels to a file
OutFile=inflowwind_library.WriteOutChans(output_file,ifwlib.output_channel_names,ifwlib.output_channel_units)
OutFile.write(allOutputChannelValues)
OutFile.end()

print("InflowWind completed.")
