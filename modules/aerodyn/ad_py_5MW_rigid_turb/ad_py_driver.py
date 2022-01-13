#*******************************************************************************
# LICENSING
# Copyright (C) 2021 National Renewable Energy Lab
#
# This file is part of AeroDyn15. 
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
# This is an exampe of Python driver code for AeroDyn with InflowWind
#
# Usage: This program gives an example for how the user calls the main
#        subroutines of AeroDyn, and thus is specific to the user
#
#FIXME:
# Basic alogrithm for using AeroDyn InflowWind python library
#   1.  initialize python wrapper library
#           set necessary library values
#           set input file string arrays (from file or script)
#   2.  initialize AeroDyn Fortran library
#           set initial position, velocity, acceleration values
#           call aerodyn_inflow_init once to initialize IfW
#           Handle any resulting errors
#   3.  timestep iteration
#           set extrapolated values for inputs
#           call aerodyn_inflow_updatestates to propogate forwared from t to t+dt
#           set position, velocity, and accleration information for all nodes
#           call aerodyn_inflow_calcoutput.  Handle any resulting errors
#           return the resulting force and moment array
#           aggregate output channnels
#   4. End
#         call aerodyn_inflow_end to close the AeroDyn library and free memory
#         handle any resulting errors
#
#
import numpy as np
import os
import sys

# path to find the aerodyn_inflow_library.py from the local directory
sys.path.insert(0, os.path.sep.join(["..", "..", "..", "..", "..", "modules", "aerodyn", "python-lib"]))
import aerodyn_inflow_library as adi        # this file handles the conversion from python to c-bound types and should not be changed by the user

###############################################################################
# Locations to build directory relative to r-test directory.  This is specific
# to the regession testing with openfast and will need to be updated when
# coupled to other codes or use cases

basename = "libaerodyn_inflow_c_binding"
if sys.platform == "linux" or sys.platform == "linux2":
    library_path = os.path.sep.join(["..", "..", "..", "..", "..", "build", "modules", "aerodyn", basename + ".so"])
elif sys.platform == "darwin":
    library_path = os.path.sep.join(["..", "..", "..", "..", "..", "build", "modules", "aerodyn", basename + ".dylib"])
elif sys.platform == "win32":
    # Windows may have this library installed in one of two locations depending
    # on which build system was used (CMake or VS).
    library_path = os.path.sep.join(["..", "..", "..", "..", "..", "build", "modules", "aerodyn", basename + ".dll"])   # cmake install location
    if not os.path.isfile(library_path) and not sys.maxsize > 2**32:        # Try VS build location otherwise
        library_path = os.path.sep.join(["..", "..", "..", "..", "..", "build", "bin", "AeroDyn_Inflow_c_lib_Win32.dll"]) # VS build install location
        if not os.path.isfile(library_path):
            print(f"Python is 32 bit and cannot find 32 bit InflowWind DLL expected at: {library_path}")
            exit(1)
    if not os.path.isfile(library_path) and sys.maxsize > 2**32:        # Try VS build location otherwise
        library_path = os.path.sep.join(["..", "..", "..", "..", "..", "build", "bin", "AeroDyn_Inflow_c_lib_x64.dll"]) # VS build install location
        if not os.path.isfile(library_path):
            print(f"Python is 64 bit and cannot find 64 bit InflowWind DLL expected at: {library_path}")
            exit(1)



###############################################################################
# For testing, a set of input files is read in.  Everything in these input
# files could in principle be hard coded into this script.  These are separated
# out for convenience in testing.

#   Primary input
#       This is identical to what AeroDyn would read from disk if we were
#       not passing it.  When coupled to other codes, this may be passed
#       directly from memory (i.e. during optimization with WEIS), or read as a
#       template and edited in memory for each iteration loop.
primary_ad_file="ad_primary.dat"
primary_ifw_file="ifw_primary.dat"

#   Debug output file
#       When coupled into another code, an array of position/orientation,
#       velocities, and accelerations are passed in, and an array of
#       Forces+Moments is returned.  For debugging, it may be useful to dump all
#       off this to file.
debugout_file="DbgOutputs.out"

#   Output file
#       When coupled to another code, the channels requested in the outlist
#       section of the output file are passed back for writing to file.  Here
#       we will write the aggregated output channels to a file at the end of
#       the simulation.
output_file="ad_py_driver.out"

#   For checking if our library is correctly handling correction steps, set
#   this to > 0
NumCorrections=0

#   Node position info for testing
node_pos_file="NodePositions.txt"
node_orient_file="NodeOrientations.txt"

#   Input Files
#===============================================================================

#   Main AeroDyn input file
#       This file is read from disk to an array of strings with the line
#       endings stripped off.  This array will have the same number of elements
#       as there are lines in the file.
adiAD_input_string_array = []     # instantiate empty array
fh = open(primary_ad_file, "r")
for line in fh:
  # strip line ending and ending white space and add to array of strings
  adiAD_input_string_array.append(line.rstrip())
fh.close()

adiIfW_input_string_array = []     # instantiate empty array
fh = open(primary_ifw_file, "r")
for line in fh:
  # strip line ending and ending white space and add to array of strings
  adiIfW_input_string_array.append(line.rstrip())
fh.close()

#   Initial node positions
#       Read in the initial node positions
initMeshPos_ar    = np.loadtxt(node_pos_file,    comments="#", unpack=False)
initMeshOrient_ar = np.loadtxt(node_orient_file, comments="#", unpack=False, dtype = np.float64)
#print("shape of initMeshPos_ar   ",   initMeshPos_ar.shape)
#print("               size 0     ",   initMeshPos_ar.shape[0])
#print("               size 1     ",   initMeshPos_ar.shape[1])
#print("shape of initMeshOrient_ar",   initMeshOrient_ar.shape)
#print("               size 0     ",   initMeshOrient_ar.shape[0])
#print("               size 1     ",   initMeshOrient_ar.shape[1])
#print("               type       ", type(initMeshOrient_ar))
#print("               float      ", type(initMeshOrient_ar[0,0]))
if np.size(initMeshPos_ar,0) != np.size(initMeshOrient_ar,0):
    print("different number of nodes in position and orientation arrays read")
    exit(1)
# For this example, we will pull the hub position/orientation and blade root
# information from the initMeshPos_ar/initMeshOrient_ar
#   hub:        index 0
#   nacelle:    set to hub for demonstration (normally at a different location)
#   root:       every numBladeNode starting at 1
initHubPos          = initMeshPos_ar[   0,:]
initHubOrient       = initMeshOrient_ar[0,:]
initNacellePos      = initMeshPos_ar[   0,:]
initNacelleOrient   = initMeshOrient_ar[0,:]
numBlades           = 3
numBladeNode        = int((initMeshPos_ar.shape[0]-1)/numBlades)
initRootPos         = np.zeros((numBlades,3))
initRootOrient      = np.zeros((numBlades,9))
for i in range(3):
    initRootPos[i,:]    = initMeshPos_ar[   i*numBladeNode+1,:]
    initRootOrient[i,:] = initMeshOrient_ar[i*numBladeNode+1,:]

#===============================================================================
#   AeroDyn python interface initialization 
#===============================================================================

#   Instantiate the hdlib python object
#       wrap this in error handling in case the library_path is incorrect
try:
    adilib = adi.AeroDynInflowLib(library_path)
except Exception as e:
    print("{}".format(e))
    print(f"Cannot load library at {library_path}")
    exit(1)

# These will be read from the AD driver input file
#   Time inputs
#           adlib.dt           -- the timestep aerodyn is called at.
#           adlib.numTimeSteps -- total number of timesteps, only used to
#                                  construct arrays to hold the output channel
#                                  info
adilib.InterpOrder   = 2          # order of the interpolation
adilib.t_start       = 0          # initial time
adilib.dt            = 0.0125     # time interval that it's being called at
final_time           = 60         # final time
adilib.gravity       =   9.80665  # Gravitational acceleration (m/s^2)
adilib.defFldDens    =     1.225  # Air density (kg/m^3)
adilib.defKinVisc    = 1.464E-05  # Kinematic viscosity of working fluid (m^2/s)
adilib.defSpdSound   =     335.0  # Speed of sound in working fluid (m/s)
adilib.defPatm       =  103500.0  # Atmospheric pressure (Pa) [used only for an MHK turbine cavitation check]
adilib.defPvap       =    1700.0  # Vapour pressure of working fluid (Pa) [used only for an MHK turbine cavitation check]
adilib.WtrDpth       =       0.0  # Water depth (m)
adilib.MSL2SWL       =       0.0  # Offset between still-water level and mean sea level (m) [positive upward]

# Setup some timekeeping
time                = np.arange(adilib.t_start,final_time + adilib.dt,adilib.dt) # total time + increment because python doesnt include endpoint!
adilib.numTimeSteps = len(time)          # only for constructing array of output channels for duration of simulation

# set WrVTK
adilib.WrVTK = 2

#==============================================================================
# Basic alogrithm for using AeroDyn+InflowWind library
#
# NOTE: the error handling here is handled locally since this is the only
#       driver code.  If AeroDyn+InflowWind is incorporated into another code,
#       the error handling will need to be passed to the main code.  That way
#       the main code can close other modules as necessary (otherwise you will
#       end up with memory leaks and a bunch of garbage in the other library
#       instances).

# Set hub and blade root positions/orientations
adilib.initHubPos           = initHubPos
adilib.initHubOrient        = initHubOrient
adilib.initNacellePos       = initNacellePos
adilib.initNacelleOrient    = initNacelleOrient
adilib.numBlades            = numBlades
#adilib.numBladeNode         = numBladeNode     # May be necessary to pass info on nodes on each blade to AD15 for mesh mapping.
adilib.initRootPos          = initRootPos
adilib.initRootOrient       = initRootOrient


# Set number of mesh nodes and initial position
#       positiion   is an N x 3 array [x,y,z]
#       orientation is a  N x 9 array [r11,r12,r13,r21,r22,r23,r31,r32,r33]
adilib.numMeshPts = np.size(initMeshPos_ar,0)
adilib.initMeshPos    = initMeshPos_ar
adilib.initMeshOrient = initMeshOrient_ar
#print("initMeshOrient float      ", type(adilib.initMeshOrient[0,0]))

print("Try call to aerodyn_inflow_init")
# AeroDyn_Inflow_Init: Only need to call aerodyn_inflow_init once
try:
    adilib.aerodyn_inflow_init(adiAD_input_string_array,adiIfW_input_string_array)
except Exception as e:
    print("{}".format(e))   # Exceptions handled in aerodyn_inflow_library.py
    #FIXME: temporary statement here
    print("Exit after failed call to aerodyn_inflow_init")
    exit(1)


#  To get the names and units of the output channels
#output_channel_names = adilib.output_channel_names
#output_channel_units = adilib.output_channel_units

#-------------------
#   Time steppping
#-------------------

#  Set the array holding the ouput channel values to zeros initially.  Output
#  channel values returned from each CalcOutput call in this array.  We will
#  aggregate them together in the time stepping loop to get the entire time
#  series.  Time channel is not included, so we must add that.
outputChannelValues = np.zeros(adilib.numChannels)
allOutputChannelValues = np.zeros( (adilib.numTimeSteps,adilib.numChannels+1) )

#  Setup the arrays for motion and resulting forces/moments - C index order
nodePos     = np.zeros((adilib.numMeshPts,3))    # [x,y,z,Rx,Ry,Rz]
nodeVel     = np.zeros((adilib.numMeshPts,6))    # [x,y,z,Rx,Ry,Rz]_dot  -- first  deriv (velocities)
nodeAcc     = np.zeros((adilib.numMeshPts,6))    # [x,y,z,Rx,Ry,Rz]_ddot -- second deriv (accelerations)
nodeFrcMom  = np.zeros((adilib.numMeshPts,6))    # [Fx,Fy,Fz,Mx,My,Mz]   -- resultant forces/moments at each node


#   Open outputfile for regession testing purposes.
dbg_outfile = aerodyn_inflow_library.DriverDbg(debugout_file,adilib.numMeshPts)


# Calculate outputs for t_initial
i=0
#nodePos[0,0:6] = adi_timeseries[i, 1: 7]     # note: python slicing stops at element before last index in range (different than fortran wich is inclusive)
#nodeVel[0,0:6] = adi_timeseries[i, 7:13]
#nodeAcc[0,0:6] = adi_timeseries[i,13:19]
try:
    adilib.aerodyn_inflow_calcOutput(time[i], nodePos, nodeVel, nodeAcc, 
            nodeFrcMom, outputChannelValues)
except Exception as e:
    print("{}".format(e))
    dbg_outfile.end()
    #FIXME: temporary statement here
    print("Exit after failed call to aerodyn_inflow_calcOutput at T=0")
    exit(1)
 
# Write the debug output at t=t_initial
dbg_outfile.write(time[i],nodePos,nodeVel,nodeAcc,nodeFrcMom)
# Save the output at t=t_initial
allOutputChannelValues[i,:] = np.append(time[i],outputChannelValues)


#   Timestep iteration
#       Correction loop:
#           1.  Set inputs at t+dt using either extrapolated values (or
#               corrected values if in a correction step) from the structural
#               solver
#           2.  Call UpdateStates to propogate states from t -> t+dt
#           3.  call Ifw_CalcOutput_C to get the resulting forces at t+dt using
#               the updated state information for t+dt.  These would be passed
#               back to the structural solver at each step of the correction
#               loop so that it can be used to tune the states of other modules
#               (structural solver etc).
#       End correction loop:
#           4.  Once correction loop is complete, save the resulting values
#
#   time[i]   is at t
#   time[i+1] is at t+dt
for i in range( 0, len(time)-1):

    #print(f"iter: {i}: {time[i]}")

    for correction in range(0, NumCorrections+1):

        #print(f"Correction step: {correction} for {time[i]} --> {time[i+1]}")

        # If there are correction steps, the inputs would be updated using outputs
        # from the other modules.
#        nodePos[0,0:6] = adi_timeseries[i+1, 1: 7]
#        nodeVel[0,0:6] = adi_timeseries[i+1, 7:13]
#        nodeAcc[0,0:6] = adi_timeseries[i+1,13:19]

        #   Update the states from t to t+dt (only if not beyond end of sim)
        try:
            adilib.aerodyn_inflow_updateStates(time[i], time[i+1], nodePos, nodeVel,
                    nodeAcc, nodeFrcMom)
        except Exception as e:
            print("{}".format(e))
            dbg_outfile.end()
            #FIXME: temporary statement here
            print("Exit after failed call to aerodyn_inflow_updateStates")
            exit(1)
 
        # Calculate the outputs at t+dt
        #       NOTE: new input values may be available at this point from the
        #       structural solver, so update them here.
#        nodePos[0,0:6] = adi_timeseries[i+1, 1: 7]
#        nodeVel[0,0:6] = adi_timeseries[i+1, 7:13]
#        nodeAcc[0,0:6] = adi_timeseries[i+1,13:19]

        try:
            adilib.aerodyn_inflow_calcOutput(time[i+1], nodePos, nodeVel, nodeAcc, 
                    nodeFrcMom, outputChannelValues)
        except Exception as e:
            print("{}".format(e))
            dbg_outfile.end()
            #FIXME: temporary statement here
            print("Exit after failed call to aerodyn_inflow_calcOutput")
            exit(1)

 
        #   When coupled to a different code, this is where the Force/Moment info
        #   would be passed to the aerodynamic solver.
        #
        #   For this regression test example, we will write this to file (in
        #   principle this could be aggregated and written out once at the end of
        #   the regression simulation, but for simplicity we are writting one line
        #   at a time during the call).  The regression test will have one row for
        #   each timestep + position array entry.
        dbg_outfile.write(time[i+1],nodePos,nodeVel,nodeAcc,nodeFrcMom)


    # Store the channel outputs -- these are requested from within the IfW input
    # file OutList section.  In OpenFAST, these are added to the output
    # channel array for all modules and written to that output file.  For this
    # example we will write to file at the end of the simulation in a single
    # shot.
    allOutputChannelValues[i+1,:] = np.append(time[i+1],outputChannelValues)


dbg_outfile.end()   # close the debug output file


# aerodyn_inflow_end: Only need to call aerodyn_inflow_end once.
#   NOTE:   in the event of an error during the above Init or CalcOutput calls,
#           the IfW_End routine will be called during that error handling.
#           This works for IfW, but may not be a desirable way to handle
#           errors in other codes (we may still want to retrieve some info
#           from memory before clearing out everything).
#   NOTE:   Error handling from the aerodyn_inflow_end call may not be entirely
#           necessary, but we may want to know if some memory was not released
#           properly or a file not closed correctly.
try:
    adilib.aerodyn_inflow_end()
except Exception as e:
    print("{}".format(e))
    #FIXME: temporary statement here
    print("Exit after failed call to aerodyn_inflow_end")
    exit(1)


#   Now write the ouput channels to a file
OutFile=aerodyn_inflow_library.WriteOutChans(output_file,adilib.output_channel_names,adilib.output_channel_units)
OutFile.write(allOutputChannelValues)
OutFile.end()



#print("HydroDyn successful.")
exit()

