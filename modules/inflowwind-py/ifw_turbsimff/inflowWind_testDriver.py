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
import sys
sys.path.insert(0, os.path.sep.join(["..", "..", "..", "..", "..", "modules", "inflowwind", "python-lib"]))
import inflowwind_library # this file handles the conversion from python to c-bound types and should not be changed by the user

#=============================================================================================================================
#------------------------------------------------------- INPUT FILES ---------------------------------------------------------
#=============================================================================================================================

# Main inflowWind input file
# Usage: the contents of this string follow the identical syntax to what is described for the inflowWind input file in the user guides and documentation
# Please modify the string contents based on your specific use case
ifw_input_string_array = [
    '*------ InflowWind v3.01.* INPUT FILE -------------------------------------------------------------------------', \
    '*Steady 15 m/s winds with no shear for IEA 15 MW Offshore Reference Turbine', \
    '*--------------------------------------------------------------------------------------------------------------', \
    '       false  Echo           - Echo input data to <RootName>.ech (flag)', \
    '          3   WindType       - switch for wind file type (1=steady; 2=uniform; 3=binary TurbSim FF; 4=binary Bladed-style FF; 5=HAWC format; 6=User defined; 7=native Bladed FF)', \
    '          0   PropagationDir - Direction of wind propagation (meteoroligical rotation from aligned with X (positive rotates towards -Y) -- degrees)', \
    '          0   VFlowAng       - Upflow angle (degrees) (not used for native Bladed format WindType=7)', \
    '          1   NWindVel       - Number of points to output the wind velocity    (0 to 9)', \
    '          0   WindVxiList    - List of coordinates in the inertial X direction (m)', \
    '          0   WindVyiList    - List of coordinates in the inertial Y direction (m)', \
    '        150   WindVziList    - List of coordinates in the inertial Z direction (m)', \
    '================== Parameters for Steady Wind Conditions [used only for WindType = 1] =========================', \
    '       15.0   HWindSpeed     - Horizontal windspeed                            (m/s)', \
    '        150   RefHt          - Reference height for horizontal wind speed      (m)', \
    '        0.0   PLexp          - Power law exponent                              (-)', \
    '================== Parameters for Uniform wind file   [used only for WindType = 2] ============================', \
    '"unused"      FileName_Uni   - Filename of time series data for uniform wind field.      (-)', \
    '        150   RefHt_Uni      - Reference height for horizontal wind speed                (m)', \
    '     125.88   RefLength      - Reference length for linear horizontal and vertical sheer (-)', \
    '================== Parameters for Binary TurbSim Full-Field files   [used only for WindType = 3] ==============', \
    '"../../../glue-codes/openfast/5MW_Baseline/Wind/90m_12mps_twr.bts"      filename_bts   - name of the full field wind file to use (.bts)', \
    '================== Parameters for Binary Bladed-style Full-Field files   [used only for WindType = 4] =========', \
    '"unused"      FilenameRoot   - Rootname of the full-field wind file to use (.wnd, .sum)', \
    'False         TowerFile      - Have tower file (.twr) (flag)', \
    '================== Parameters for HAWC-format binary files  [Only used with WindType = 5] =====================', \
    '"unused"      FileName_u     - name of the file containing the u-component fluctuating wind (.bin)', \
    '"unused"      FileName_v     - name of the file containing the v-component fluctuating wind (.bin)', \
    '"unused"      FileName_w     - name of the file containing the w-component fluctuating wind (.bin)', \
    '         64   nx             - number of grids in the x direction (in the 3 files above) (-)', \
    '         32   ny             - number of grids in the y direction (in the 3 files above) (-)', \
    '         32   nz             - number of grids in the z direction (in the 3 files above) (-)', \
    '         16   dx             - distance (in meters) between points in the x direction    (m)', \
    '          3   dy             - distance (in meters) between points in the y direction    (m)', \
    '          3   dz             - distance (in meters) between points in the z direction    (m)', \
    '        150   RefHt_HAWC     - reference height; the height (in meters) of the vertical center of the grid (m)', \
    ' -------------   Scaling parameters for turbulence   ---------------------------------------------------------', \
    '          2   ScaleMethod    - Turbulence scaling method   [0 = none, 1 = direct scaling, 2 = calculate scaling factor based on a desired standard deviation]', \
    '          1   SFx            - Turbulence scaling factor for the x direction (-)   [ScaleMethod=1]', \
    '          1   SFy            - Turbulence scaling factor for the y direction (-)   [ScaleMethod=1]', \
    '          1   SFz            - Turbulence scaling factor for the z direction (-)   [ScaleMethod=1]', \
    '        1.2   SigmaFx        - Turbulence standard deviation to calculate scaling from in x direction (m/s)    [ScaleMethod=2]', \
    '        0.8   SigmaFy        - Turbulence standard deviation to calculate scaling from in y direction (m/s)    [ScaleMethod=2]', \
    '        0.2   SigmaFz        - Turbulence standard deviation to calculate scaling from in z direction (m/s)    [ScaleMethod=2]', \
    '  -------------   Mean wind profile parameters (added to HAWC-format files)   ---------------------------------', \
    '         12   URef           - Mean u-component wind speed at the reference height (m/s)', \
    '          2   WindProfile    - Wind profile type (0=constant;1=logarithmic,2=power law)', \
    '        0.2   PLExp_HAWC     - Power law exponent (-) (used for PL wind profile type only)', \
    '       0.03   Z0             - Surface roughness length (m) (used for LG wind profile type only)', \
    '          0   XOffset        - Initial offset in +x direction (shift of wind box)', \
    '====================== OUTPUT ==================================================', \
    'False         SumPrint       - Print summary data to <RootName>.IfW.sum (flag)', \
    '              OutList        - The next line(s) contains a list of output parameters.  See OutListParameters.xlsx for a listing of available output channels, (-)', \
    '"Wind1VelX,Wind1VelY,Wind1VelZ"     - Wind velocity at point WindVxiList(1),WindVyiList(1),WindVziList(1).  X, Y, and Z direction components.', \
    'END of input file (the word "END" must appear in the first 3 columns of this last OutList line)', \
    '---------------------------------------------------------------------------------------'
]

#----------------------------------------------------------------------------------------------------------------------------------

# Uniform wind input file - only needed for WindType = 2
# Usage: Please modify the string contents based on your specific use case. Syntax follows user guides and documentation. Must have as input.
ifw_uniform_string_array = [ 
    '! OpenFAST InflowWind uniform wind input file for 15 m/s wind.',  \
    '! Time Wind  Wind  Vert. Horiz. Vert. LinV  Gust   Upflow',  \
    '!      Speed Dir   Speed Shear  Shear Shear Speed  Angle',  \
    '! (sec) (m/s) (deg) (m/s) (-)    (-)   (-)  (m/s)  (deg)',  \
    '  0.0  15.0  0.0   0.0   0.0    0.0   0.0   0.0    0.0',  \
    '  0.1  15.0  0.0   0.0   0.0    0.0   0.0   0.0    0.0',  \
    '  1.0  15.0  0.0   0.0   0.0    0.0   0.0   0.0    0.0'
]

#=============================================================================================================================
#----------------------------------------------------- FUNCTION CALLS --------------------------------------------------------
#=============================================================================================================================

# Call the InflowWind API
# User must modify this path to point to the shared library
#FIXME: generalize the path for cross platform
library_path = os.path.sep.join(["..", "..", "..", "..", "..", "install", "lib", "libifw_c_lib.dylib"])
ifwlib = inflowwind_library.InflowWindLibAPI(library_path)

#FIXME: can we generalize this to use the same driver input file?  if not, can we make an input file for this?
# Time inputs - user adjusts as needed/desired
t_start             = 0                  # initial time
ifwlib.dt           = 0.1                # time interval that it's being called at, not usedby IFW, only here for consistency with other modules
ifwlib.total_time   = 1                  # final or total time
time                = np.arange(t_start,ifwlib.total_time + ifwlib.dt,ifwlib.dt) # total time + increment because python doesnt include endpoint!
ifwlib.numTimeSteps = len(time)

# Initialize arrays
# User shall update the positions array for each time step for their application. 
# Coordinates are N x 3 ([x, y, z]) in the openfast global coordinate system (aka inertial coordinates). 
positions = np.array([
    [0.0,  0.0, 50],
    [0.0,  0.0, 25],
    [0.0,  0.0, 75],
    [0.0,  25., 50],
    [0.0, -25., 50],
    [0.0,  25., 75],
    [0.0, -25., 75],
    [0.0,  25., 25],
    [0.0, -25., 25]
]) 
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

# IFW_CALCOUTPUT: Loop over ifw_calcOutput as many times as needed/desired by user
idx = 0
for t in time:
    try:
        ifwlib.ifw_calcOutput(t, positions, velocities, outputChannelValues)
    except Exception as e:
        print("{}".format(e))
        exit(1)
    
    # velocities is the desired output from inflowWind that the user will need to store somewhere
    # Store the channel outputs
    ifwlib._channel_output_array = outputChannelValues
    ifwlib._channel_output_values[idx,:] = ifwlib._channel_output_array
    idx = idx + 1

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

