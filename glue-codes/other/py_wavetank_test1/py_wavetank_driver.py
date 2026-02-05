#-------------------------------------------------------------------------------
# Overview of WaveTankTesting python driver
#-------------------------------------------------------------------------------
# This script serves as a Python driver for the WaveTankTesting library. It demonstrates
# how to interact with the main subroutines of WaveTankTesting.
#
# NOTE: This script serves as a template and can be customized to meet
# individual requirements. It is not a general purpose script, so modifications
# will be necessary for more general usage.  It was developed only to verify
# that the interface for WaveTankTesting that gets used with LabView doesn't
# get accidentally broken


#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from ctypes import c_void_p

import numpy as np
from pyOpenFAST import wavetanktesting as wtt
from pyOpenFAST.tdmslib import TdmsToDict 

#--------------------------------------
# Library paths
#--------------------------------------
# Path to find the driver_utilities.py module from the local directory
#
# NOTE: This file contains helper functions to assist with the driver codes
# across different modules
modules_path = Path(__file__).parent.joinpath(*[".."]*5, "reg_tests", "r-test", "modules")
print(f"Importing 'driver_utilities' from {modules_path}")
sys.path.insert(0, str(modules_path))
from driver_utilities import *



if __name__=="__main__":

    # Read a motion series from a prior tank run
    TDMSfile="0822_4.tdms"
    floater_motions = TdmsToDict(TDMSfile)["Winch System"]

    n_timesteps_max = len(floater_motions["x"])

    # set sim time for test case
    dt = 0.1   # seconds
    tmax = 5   # seconds -- to make this test short enough to run
    n_timesteps = min(int(tmax / dt), n_timesteps_max)

    # load and initialize
    try:
        wtlib = wtt.WaveTankLib(get_library_path(module_name="wavetanktesting"))
    except Exception as e:
        print(f"Failed to load library: {e}")
        sys.exit(1)

    wtlib.init({"WaveTankConfig":   "wavetankconfig.in",})

    # output everything going through interface
    if wtlib.debug_outputs:
        debug_output_file = wtt.DriverDbg(
            wtlib.debug_output_file
        )


 
    for i in range(n_timesteps):

        if i==0:
            print(f"        tmax = {tmax}")

        time = dt*i
        print(f"            t = {time}")

        # position/orientation
        x=floater_motions["x"][i]
        y=floater_motions["y"][i]
        z=floater_motions["z"][i]
        r=floater_motions["phi"][i]
        p=floater_motions["theta"][i]
        y=floater_motions["psi"][i]
        pos = np.array([x, y, z, r, p, y], dtype=np.float32)

        # vel 
        x_dot=floater_motions["x_dot"][i]
        y_dot=floater_motions["y_dot"][i]
        z_dot=floater_motions["z_dot"][i]
        r_dot=floater_motions["phi_dot"][i]
        p_dot=floater_motions["theta_dot"][i]
        y_dot=floater_motions["psi_dot"][i]
        vel = np.array([x_dot, y_dot, z_dot, r_dot, p_dot, y_dot], dtype=np.float32)

        # acc 
        x_ddot=floater_motions["x_ddot"][i]
        y_ddot=floater_motions["y_ddot"][i]
        z_ddot=floater_motions["z_ddot"][i]
        r_ddot=floater_motions["phi_ddot"][i]
        p_ddot=floater_motions["theta_ddot"][i]
        y_ddot=floater_motions["psi_ddot"][i]
        acc = np.array([x_ddot, y_ddot, z_ddot, r_ddot, p_ddot, y_ddot], dtype=np.float32)

        #vel=pos
        #acc=pos
        body_motion=wtt.MotionData(pos,vel,acc)
        body_loads=wtt.LoadsData(np.array([0, 0, 0, 0, 0, 0], dtype=np.float32))

        wtlib.calc_step(
            time,
            body_motion,
            body_loads,
        )

        # Write debug output if enabled
        if wtlib.debug_outputs:
            debug_output_file.write(
                time, body_motion, body_loads
            )



    # Close debug output file if it was opened
    if wtlib.debug_outputs:
        debug_output_file.end()


    wtlib.end()

    print("WaveTankTesting run completed")


