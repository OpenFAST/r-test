#-------------------------------------------------------------------------------
# LICENSING
#-------------------------------------------------------------------------------
# Copyright (C) 2025-present by National Renewable Energy Lab (NREL)
#
# This file is part of SeaState
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

#-------------------------------------------------------------------------------
# Overview of SeaState python driver
#-------------------------------------------------------------------------------
# This script serves as a Python driver for the SeaState library. It demonstrates
# how to interact with the main subroutines of SeaState.
#
# NOTE: This script serves as a template and can be customized to meet
# individual requirements.
#
# Basic algorithm for using SeaState python library:
#   1. Initialize the Python wrapper library:
#      - Set necessary library values
#      - Load input file data (from file/script)
#   2. Initialize the SeaState Fortran library:
#      - Call seastate_init once
#      - Handle any resulting errors
#   3. Sample call at a few different times/positions 
#      - Set array of positions
#      - Call seastate_calcoutput and handle errors
#      - Return resulting velocities array
#      - Aggregate output channels
#   4. call a few other interface routines to check if they work
#FIXME: finalize names after interface finalized a bit more
#      - GetWaveFieldPointer
#      - get_fluidVelAccDens for a few points
#   4. Finalize:
#      - Call ifw_end to close library and release resources
#      - Handle any resulting errors

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
from pyOpenFAST import seastate

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

#-------------------------------------------------------------------------------
# Configuration classes containing problem inputs
#-------------------------------------------------------------------------------
@dataclass
class SeaStateConfig:
    """Configuration settings for SeaState simulation."""
    # Time settings
    #
    # For this test case, we are checking between 30 and 30.8 seconds.  The
    # seastate python library interface must be informed about the
    # following 2 time related information variables
    #   - ifwlib.dt -> timestep seastate is called at
    #   - ifwlib.time_max -> total simulation time
    #     arrays to hold the output channel
    t_start: float = 30.0   # initial time
    t_final: float = 48.0   # final time
    dt: float = 1.375       # time interval that ifw is being called at

    # Debug settings
    debug_level: int = 0  # 0-4

    # File names
    #
    # Primary input: This is identical to what SeaState would read from disk if we were not
    # passing it. When coupled to other codes, this may be passed directly from memory (i.e.
    # during optimization with WEIS), or read as a template and edited in memory for each
    # iteration loop.
    primary_ss_file: str = "SeaState.dat"

    # Position input: Contains an array of points (Nx3 [X,Y,Z] values) that will be passed to
    # SeaState at each timestep. When coupled to other codes, these positions would be passed
    # directly from the structural code instead of reading from a file.
    points_file: str = "Points.inp"

    # Velocities output: For testing/debugging, the calculated velocities at each position point
    # are written to this file. When coupled to other codes, these velocities would be returned
    # directly to the calling code instead of writing to file.
    results_file: str = "Points.Results.dat"

    # Output channels: Contains the aggregated output channels requested in the outlist section.
    # When coupled to other codes, these values could be passed back for writing by the calling
    # code instead of writing directly to file here.
    output_file: str = "py_seastate.out"

    # SS pointer
    ss_pointer = c_void_p(None)

    # VTK settings
    vtk_write: int = 0      # 0: none, 1: init, 2: animation
    vtk_dt:float = 0.25
    vtk_output_dir: str = "vtk"

#-------------------------------------------------------------------------------
# Main driver class
#-------------------------------------------------------------------------------
class SeaStateDriver:
    """Main driver class for SeaState simulation."""

    def __init__(self, config: SeaStateConfig):
        """Initialize the SeaState driver.

        Args:
            config: Configuration settings for the simulation
        """
        self.config = config

        # Initialize data structures
        self.time = np.linspace(
            self.config.t_start,
            self.config.t_final,
            int((self.config.t_final - self.config.t_start) / self.config.dt) + 1
        )

        # Initialize library
        self.sslib = self._initialize_library()

    def _initialize_library(self) -> seastate.SeaStateLib:
        """Initialize the SeaState library with configuration settings.

        Returns:
            Configured instance of the SeaState library

        Raises:
            SystemExit: If library initialization fails
        """
        try:
            sslib = seastate.SeaStateLib(get_library_path(module_name="seastate"))
        except Exception as e:
            print(f"Failed to load library: {e}")
            sys.exit(1)

        # Configure library
        #
        # sslib.dt -> timestep seastate is called at
        sslib.dt = self.config.dt
        # sslib.numTimeSteps -> total number of timesteps, used to construct arrays to hold the output channel
        sslib.time_max = self.config.t_final
        # sslib.debuglevel -> debug level for IfW library
        sslib.debuglevel = self.config.debug_level

        # configure vtk
        sslib.vtk_write = self.config.vtk_write
        sslib.vtk_dt    = self.config.vtk_dt
        sslib.vtk_output_dir = self.config.vtk_output_dir

        return sslib

    def run_simulation(self) -> None:
        """Run the main simulation loop."""
        # Slurp in the points file
        try:
            self.points_array = np.loadtxt(self.config.points_file, comments='#')
            self.results_array = np.zeros((self.points_array.shape[0], 3))
        except Exception as e:
            print(f"failed in reading {self.points_file}: {e}")
            sys.exit(1)

        # Pre initialize (sets environment vars)
        self.sslib.debug_level = self.config.debug_level
        try:
            self.sslib.seastate_preinit()
        except Exception as e:
            print(f"seastate_preinit failed: {e}")
            sys.exit(1)

        # Initialize SeaState
        try:
            # Initialize SeaState -> only need to call it once
            #FIXME: need to set some vars
            self.sslib.seastate_init(self.config.primary_ss_file)
        except Exception as e:
            print(f"seastate_init failed: {e}")
            sys.exit(1)

        # Initialize output arrays
        output_channel_values = np.zeros(self.sslib.numChannels)
        all_output_channel_values = np.zeros((len(self.time), self.sslib.numChannels + 1))

        # setup the results file
        results_output = seastate.ResultsOut(
            self.config.results_file,
            self.sslib.numChannels
        )

        # sslib.numuResPts -> total number of points requesting for at each time step
        self.numuResPts = self.results_array.shape[0]

        # get the pointer to the WaveField data
        try:
            self.sslib.seastate_getWaveFieldPointer(self.config.ss_pointer)
            print(f"py_seastate_driver: Retrieving pointer to WaveField data: {self.config.ss_pointer.value}")
        except Exception as e:
            print(f"Failed to retrieve the WaveField pointer")
            sys.exit(1)

        # set the pointer to the WaveField data
        # This is to test if we can actually set a pointer from externally
        try:
            print(f"py_seastate_driver: Setting pointer to WaveField data: {self.config.ss_pointer.value}")
            self.sslib.seastate_setWaveFieldPointer(self.config.ss_pointer)
        except Exception as e:
            print(f"Failed to Set the WaveField pointer")
            sys.exit(1)

        # get the min and max wave elvation
        try:
            elevMin: float = 0.0
            elevMax: float = 0.0
            elevMin,elevMax = self.sslib.get_elevMinMax()
            print(f"py_seastate_driver: Min wave elevation {elevMin}; max wave elevation {elevMax}")
        except Exception as e:
            print(f"Failed to get the WaveField min and max elevations")
            sys.exit(1)


        try:
            # Time stepping loop: step through all the timesteps
            #   1. Set the positions array with node positions from the structural solver
            #   2. Call seastate_calcOutput to retrieve the corresponding velocities
            #      to pass back to the calling code (or write to disk in this example)
            for i, t in enumerate(self.time):
                print(f"        t = {t}")
                # NOTE: When coupled to another code, set the positions info for this
                # timestep here in the calling algorithm. For this regression test example,
                # the positions are kept constant throughout the simulation.

                try:
                    self.sslib.seastate_calcOutput(
                        t,
                        output_channel_values
                    )
                except Exception as e:
                    print(f"Error in calculation at t={t}: {e}")
                    raise

                # Store the channel outputs requested in the SeaState input file's OutList section.
                # In OpenFAST, these would be added to the output channel array for all modules.
                # Here we store them with the timestamp for writing to file at the end of simulation.
                all_output_channel_values[i,:] = np.append(t, output_channel_values)

                # cycle through all points
                for j in range(self.numuResPts):
                    vel = np.zeros((3,), dtype=float)
                    acc = np.zeros((3,), dtype=float)
                    nodeInWater: int = 0
                    elev: float = 0.0
                    normVec = np.zeros((3,), dtype=float)
                    # get the fluid velocity/acceleration
                    try:
                        pos = self.points_array[j]
                        vel,acc,nodeInWater = self.sslib.get_fluidVelAcc(
                            t,
                            pos,
                            vel,
                            acc,
                            nodeInWater
                        )
                    except Exception as e:
                        print(f"Error in getting fluid velocity and acceleration  at t={t} for {pos}: {e}")
                        raise

                    # get the wave elevation at the point
                    try:
                        pos = self.points_array[j]
                        elev = self.sslib.get_surfElev(
                            t,
                            pos,
                            elev,
                        )
                    except Exception as e:
                        print(f"Error in getting surface elevation at t={t} for {pos}: {e}")
                        raise

                    # get the normal to the wave surface at the point
                    try:
                        pos = self.points_array[j]
                        normVec = self.sslib.get_surfNorm(
                            t,
                            pos,
                            normVec,
                        )
                    except Exception as e:
                        print(f"Error in getting surface normal vector at t={t} for {pos}: {e}")
                        raise

                    # Write debug output (positions and velocities) for each timestep.
                    # This is primarily used for regression testing, writing one row
                    # for each timestep + position array entry.
                    results_output.write(t, pos, vel, acc, nodeInWater, elev, normVec)

        finally:
            # Close the results file
            results_output.end()

            # Call seastate_end to clean up resources
            # NOTE: seastate_end is automatically called during error handling of seastate_init and
            # seastate_calc_output. While this works for SeaState, other modules might need
            # to retrieve data from memory before cleanup.
            self.sslib.seastate_end()

        # Write final outputs
        out_file = seastate.WriteOutChans(
            self.config.output_file,
            self.sslib.output_channel_names,
            self.sslib.output_channel_units
        )
        out_file.write(all_output_channel_values)
        out_file.end()

        print("SeaState completed successfully")

if __name__ == "__main__":
    driver = SeaStateDriver(SeaStateConfig())
    driver.run_simulation()
