#*******************************************************************************
# LICENSING
# Copyright (C) 2021 National Renewable Energy Lab
#
# This file is part of HydroDyn. 
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
# This is an exampe of Python driver code for HydroDyn (this will be replaced
# by a full Python driver with the same functionality as the HydroDyn Fortran
# driver).
#
# Usage: This program gives an example for how the user calls the main
#        subroutines of HydroDyn, and thus is specific to the user
#
# Basic alogrithm for using HydroDyn python library
#   1.  initialize python wrapper library
#           set necessary library values
#           set input file string arrays (from file or script)
#   2.  initialize HydroDyn Fortran library
#           set initial position, velocity, acceleration values
#           call hydrodyn_init once to initialize IfW
#           Handle any resulting errors
#   3.  timestep iteration
#           set extrapolated values for inputs
#           call hydrodyn_updatestates to propogate forwared from t to t+dt
#           set position, velocity, and accleration information for all nodes
#           call hydrodybn_calcoutput.  Handle any resulting errors
#           return the resulting force and moment array
#           aggregate output channnels
#   4. End
#         call hydrodyn_end to close the HydroDyn library and free memory
#         handle any resulting errors
#
#
import numpy as np
import os
import datetime
import sys

# path to find the hydrodyn_library.py from the local directory
sys.path.insert(0, os.path.sep.join(["..", "..", "..", "..", "..", "modules", "hydrodyn", "python-lib"]))
import hydrodyn_library # this file handles the conversion from python to c-bound types and should not be changed by the user

###############################################################################
# Locations to build directory relative to r-test directory.  This is specific
# to the regession testing with openfast and will need to be updated when
# coupled to other codes or use cases
if sys.platform == "linux" or sys.platform == "linux2":
    library_path = os.path.sep.join(["..", "..", "..", "..", "..", "install", "lib", "libhydrodyn_c_lib.so"])
elif sys.platform == "darwin":
    library_path = os.path.sep.join(["..", "..", "..", "..", "..", "install", "lib", "libhydrodyn_c_lib.dylib"])
elif sys.platform == "win32":
    # Windows may have this library installed in one of two locations depending
    # on which build system was used (CMake or VS).
    library_path = os.path.sep.join(["..", "..", "..", "..", "..", "install", "lib", "libhydrodyn_c_lib.dll"])   # cmake install location 
    if not os.path.isfile(library_path):        # Try VS build location otherwise
        library_path = os.path.sep.join(["..", "..", "..", "..", "..", "build", "bin", "libhydrodyn_c_lib.dll"]) # VS build install location


###############################################################################
# For testing, a set of input files is read in.  Everything in these input
# files could in principle be hard coded into this script.  These are separated
# out for convenience in testing.

#   Primary input
#       This is identical to what HydroDyn would read from disk if we were
#       not passing it.  When coupled to other codes, this may be passed
#       directly from memory (i.e. during optimization with WEIS), or read as a
#       template and edited in memory for each iteration loop.
primary_file="NRELOffshrBsline5MW_OC4DeepCwindSemi_HydroDyn.dat"

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
output_file="ifw_primary.out"


#===============================================================================
#   Helper class for debugging the interface.  This will write out all the
#   input position/orientation, velocities, accelerations, and the resulting
#   forces and moments at each input node.  If all is functioning correctly,
#   this will be identical to the corresponding values in the HydroDyn output
#   channels. 

class HydroDynDriverDbg():
    """
    This is only for debugging purposes only.  The input motions and resulting
    forces can be written to file with this class to verify the data I/O to the
    Fortran library.
    When coupled to another code, the force/moment array would be passed back
    to the calling code for use in the structural solver.  
    """
    def __init__(self,filename):
        self.DbgFile=open(filename,'wt')        # open output file and write header info
        # write file header
        t_string=datetime.datetime.now()
        dt_string=datetime.date.today()
#        self.DbgFile.write(f"## This file was generated by InflowWind_Driver on {dt_string.strftime('%b-%d-%Y')} at {t_string.strftime('%H:%M:%S')}\n")
#        self.DbgFile.write(f"## This file contains the wind velocity at the {ifwlib.numWindPts} points specified in the file ")
#        self.DbgFile.write(f"{filename}\n")
#        self.DbgFile.write("#\n")
#        self.DbgFile.write("#        T                X                Y                Z                U                V                W\n")
#        self.DbgFile.write("#       (s)              (m)              (m)              (m)             (m/s)            (m/s)            (m/s)\n")
#        self.opened = True

#    def write(self,t,positions,velocities):
#        for p, v in zip(positions,velocities):
#            self.DbgFile.write('  %14.7f   %14.7f   %14.7f   %14.7f   %14.7f   %14.7f   %14.7f\n' % (t,p[0],p[1],p[2],v[0],v[1],v[2]))

    def end(self):
        if self.opened:
            self.DbgFile.close()
            self.opened = False


#===============================================================================
#   Helper class for writing channels to file. 
#   for the regression testing to mirror the output from the InfowWind Fortran
#   driver.  This may also have value for debugging the interfacing to IfW.

class WriteOutChans():
    """
    This is only for testing purposes. Since we are not returning the
    output channels to anything, we will write them to file.  When coupled to
    another code, this data would be passed back for inclusion the any output
    file there.
    """
    def __init__(self,filename,chan_names,chan_units):
        self.OutFile=open(filename,'wt')        # open output file and write header info
        # write file header
        t_string=datetime.datetime.now()
        dt_string=datetime.date.today()
        self.OutFile.write(f"## This file was generated by InflowWind_Driver on {dt_string.strftime('%b-%d-%Y')} at {t_string.strftime('%H:%M:%S')}\n")
        self.OutFile.write(f"## This file contains output channels requested from the OutList section of the input file")
        self.OutFile.write(f"{filename}\n")
        self.OutFile.write("#\n")
        self.OutFile.write("#\n")
        self.OutFile.write("#\n")
        self.OutFile.write("#\n")
        self.OutFile.write('                Time')
        for data in chan_names:
            self.OutFile.write('%20s' % data)
        self.OutFile.write("\n")    # end line for chan_names
        self.OutFile.write('                 (s)')
        for data in chan_units:
            self.OutFile.write('%20s' % data)
        self.OutFile.write("\n")    # end line for chan_units
        self.opened = True

    def write(self,chan_data):
        l = chan_data.shape[1]
        f_string = "{:20.7f}"*l
        for i in range(chan_data.shape[0]):
            self.OutFile.write(f_string.format(*chan_data[i,:]) + '\n')

    def end(self):
        if self.opened:
            self.OutFile.close()
            self.opened = False

 

#===============================================================================
#   Input Files
#===============================================================================

#   Main HydroDyn input file
#       This file is read from disk to an array of strings with the line
#       endings stripped off.  This array will have the same number of elements
#       as there are lines in the file.
hd_input_string_array = []     # instantiate empty array
fh = open(primary_file, "r")
for line in fh:
  # strip line ending and ending white space and add to array of strings
  hd_input_string_array.append(line.rstrip())
fh.close()


#===============================================================================
#   HydroDyn python interface initialization 
#===============================================================================

#   Instantiate the hdlib python object
#       wrap this in error handling in case the library_path is incorrect
try:
    hdlib = hydrodyn_library.HydroDynLib(library_path)
except:
    print(f"Cannot load library at {library_path}")
    exit(1)

# These will be read from the HD driver input file
#   Time inputs
#           hdlib.dt           -- the timestep inflowwind is called at.
#           hdlib.numTimeSteps -- total number of timesteps, only used to
#                                  construct arrays to hold the output channel
#                                  info
t_start             = 30                 # initial time
hdlib.dt            = 0.0125             # time interval that it's being called at
final_time          = 30.1               # final time
time                = np.arange(t_start,final_time + hdlib.dt,hdlib.dt) # total time + increment because python doesnt include endpoint!
hdlib.numTimeSteps = len(time)          # only for constructing array of output channels for duration of simulation



#==============================================================================
# Basic alogrithm for using HydroDyn library
#
# NOTE: the error handling here is handled locally since this is the only
#       driver code.  If HydroDyn is incorporated into another code, the
#       error handling will need to be passed to the main code.  That way the
#       main code can close other modules as necessary (otherwise you will end
#       up with memory leaks and a bunch of garbage in the other library
#       instances).



# HydroDyn_Init: Only need to call hydrodyn_init once
try:
    hdlib.hydrodyn_init(hd_input_string_array)
except Exception as e:
    print("{}".format(e))   # Exceptions handled in hydrodyn_library.py
    exit(1)


#  To get the names and units of the output channels
#output_channel_names = hdlib.output_channel_names
#output_channel_units = hdlib.output_channel_units

#-------------------
#   Time steppping
#-------------------

#  Set the array holding the ouput channel values to zeros initially.  Output
#  channel values returned from each CalcOutput call in this array.  We will
#  aggregate them together in the time stepping loop to get the entire time
#  series.  Time channel is not included, so we must add that.
outputChannelValues = np.zeros(hdlib.numChannels)
allOutputChannelValues = np.zeros( (hdlib.numTimeSteps,hdlib.numChannels+1) )


#   Open outputfile for regession testing purposes.
dbg_outfile = HydroDynDriverDbg(debugout_file)


#   Timestep iteration
#       Step through all the timesteps.
#           1.  set the positions array with node positions from the structural
#               solver
#           2.  call Ifw_CalcOutput_C to retreive the corresponding velocities
#               to pass back to the calling code (or write to disk in this
#               example).
#
for i in range( 0, len(time)):

    #   When coupled to another code, set the motion info for this timestep
    #   here in the calling algorithm.

    try:
        #hdlib.hydrodyn_calcOutput(time[i], outputChannelValues)
        hdlib.hydrodyn_calcOutput(time[i])
    except Exception as e:
        print("{}".format(e))
        dbg_outfile.end()
        exit(1)
 
    #try:
    #    hdlib.hydrodyn_updateStates(time[i], outputChannelValues)

    #   When coupled to a different code, this is where the Force/Moment info
    #   would be passed to the aerodynamic solver.
    #
    #   For this regression test example, we will write this to file (in
    #   principle this could be aggregated and written out once at the end of
    #   the regression simulation, but for simplicity we are writting one line
    #   at a time during the call).  The regression test will have one row for
    #   each timestep + position array entry.
#    dbg_outfile.write(time[i],positions,velocities)


    # Store the channel outputs -- these are requested from within the IfW input
    # file OutList section.  In OpenFAST, these are added to the output
    # channel array for all modules and written to that output file.  For this
    # example we will write to file at the end of the simulation in a single
    # shot.
    allOutputChannelValues[i,:] = np.append(time[i],outputChannelValues)


dbg_outfile.end()   # close the regression test example output file


# hydrodyn_end: Only need to call hydrodyn_end once.
#   NOTE:   in the event of an error during the above Init or CalcOutput calls,
#           the IfW_End routine will be called during that error handling.
#           This works for IfW, but may not be a desirable way to handle
#           errors in other codes (we may still want to retrieve some info
#           from memory before clearing out everything).
#   NOTE:   Error handling from the hydrodyn_end call may not be entirely
#           necessary, but we may want to know if some memory was not released
#           properly or a file not closed correctly.
try:
    hdlib.hydrodyn_end()
except Exception as e:
    print("{}".format(e))
    exit(1)


#   Now write the ouput channels to a file
OutFile=WriteOutChans(output_file,hdlib.output_channel_names,hdlib.output_channel_units)
OutFile.write(allOutputChannelValues)
OutFile.end()



print("HydroDyn successful.")
exit()

