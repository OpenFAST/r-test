#-------------------------------------------------------------------------------
# LICENSING
#-------------------------------------------------------------------------------
# Copyright (C) 2021-present by National Renewable Energy Lab (NREL)
#
# This file is part of HydroDyn
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
# Overview of HydroDyn python driver
#-------------------------------------------------------------------------------
# This script serves as a Python driver for the HydroDyn library. It demonstrates
# how to interact with the main subroutines of HydroDyn.
#
# NOTE: This script serves as a template and can be customized to meet
# individual requirements.
#
# Basic algorithm for using HydroDyn python library:
#   1. Initialize the Python wrapper library:
#      - Set necessary library values
#      - Set input file string arrays (from file/script)
#
#   2. Initialize the HydroDyn Fortran library (i.e. C-bindings interface)
#      - Set initial position, velocity, and acceleration values
#      - Call hydrodyn_init once to initialize HydroDyn
#      - Handle any resulting errors
#
#   3. Timestep iteration:
#      - Set extrapolated values for inputs
#      - Call hydrodyn_updatestates to propagate forward from t to t+dt
#      - Set position, velocity, and acceleration information for all nodes
#      - Call hydrodyn_calcoutput. Handle any resulting errors
#      - Return the resulting force and moment array
#      - Aggregate output channels
#
#   4. End:
#      - Call hydrodyn_end to close the HydroDyn library and free memory
#      - Handle any resulting errors

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import numpy as np
from pyOpenFAST import hydrodyn

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
class HydroDynConfig:
    """Configuration settings for HydroDyn simulation."""
    num_nodes: int = 1         # Number of nodes
    num_corrections: int = 0   # Number of correction steps to perform
    debug_outputs: int = 1     # For checking the interface, set this to 1

    #--------------------------------------
    # File names
    #--------------------------------------
    # Primary input files: These files are identical to what HydroDyn would read from disk if not
    # passed directly. When coupled with other codes, they may be passed directly from memory
    # (e.g., during optimization with WEIS), or read as a template and edited in memory for each
    # iteration loop.
    seastate_primary_file: str = "NRELOffshrBsline5MW_OC4DeepCwindSemi_SeaState.dat"
    hd_primary_file: str = "NRELOffshrBsline5MW_OC4DeepCwindSemi_HydroDyn.dat"
    # Debug output file: This file is used for debugging purposes. When coupled with another code,
    # an array of position/orientation, velocities, and accelerations are passed in, and an array of
    # Forces + Moments is returned. It may be useful to dump all of this information to a file for
    # debugging.
    debug_output_file: str = "DbgOutputs.out"
    # Output file: When coupled with another code, the channels requested in the outlist section of
    # the output file are passed back for writing to a file. Here, we will write the aggregated
    # output channels to a file at the end of the simulation.
    output_file: str = "py_hd.out"
    # Time-series file: This file contains the time series data of motions
    timeseries_file: str = "OpenFAST_DisplacementTimeseries.dat"

@dataclass
class LibraryConfig:
    """Configuration settings for HydroDyn library."""
    interpolation_order: int = 1       # Order of the interpolation
    time_start: float = 0.             # Initial time
    time_final: float = 60.            # Final time
    time_interval: float = 0.0125      # Time interval for HydroDyn calls
    gravity: float = 9.80665           # Gravity (m/s^2)
    water_density: float = 1025.       # Water density (kg/m^3)
    water_depth: float = 200.          # Water depth (m)
    mean_sea_level_offset: float = 0.  # Offset between still-water level and mean sea level (m) [positive upward]

#-------------------------------------------------------------------------------
# Main driver class
#-------------------------------------------------------------------------------
class HydroDynDriver:
    """Main driver class for HydroDyn simulation."""

    def __init__(self, config: HydroDynConfig, lib_config: LibraryConfig):
        """Initialize the HydroDyn driver.

        Args:
            config: Configuration settings for the simulation
            lib_config: Configuration settings for the library
        """
        self.config = config
        self.lib_config = lib_config

        # Calculate time steps
        self.time = np.arange(
            self.lib_config.time_start,
            self.lib_config.time_final + self.lib_config.time_interval,
            self.lib_config.time_interval
        )

        # Initialize data arrays
        self._initialize_arrays()

        # Load timeseries data
        # hd_timeseries = np.genfromtxt(Path(__file__).parent / 'OpenFAST_DisplacementTimeseries.dat', delimiter=",")
        self.timeseries = np.genfromtxt(self.config.timeseries_file, delimiter=",")

        # Initialize library
        self.hdlib = self._initialize_library()

    def _initialize_arrays(self) -> None:
        """Initialize arrays for storing node kinematics and resulting loads.

        Creates zero-initialized NumPy arrays to store position, velocity, acceleration,
        and resulting force/moment data for each node in the simulation. Each array has shape
        (num_nodes, 6) where the second dimension represents:

        Kinematics arrays (positions, velocities, accelerations):
            - Translation: [x, y, z]
            - Rotation: [Rx, Ry, Rz]

        Loads array (forces_moments):
            - Forces: [Fx, Fy, Fz]
            - Moments: [Mx, My, Mz]

        All arrays use C-based index order to the C-bindings of the hydrodyn.
        """
        self.node_positions = np.zeros((self.config.num_nodes, 6))      # Translations and rotations
        self.node_velocities = np.zeros((self.config.num_nodes, 6))     # First derivatives of position
        self.node_accelerations = np.zeros((self.config.num_nodes, 6))  # Second derivatives of position
        self.node_forces_moments = np.zeros((self.config.num_nodes, 6)) # Resulting loads

    def _initialize_library(self) -> hydrodyn.HydroDynLib:
        """Initialize the HydroDyn library.

        Returns:
            HydroDynLib: Configured instance of the HydroDyn library

        Raises:
            SystemExit: If library initialization fails
        """
        try:
            # hdlib = hydrodyn.HydroDynLib(str(Path(library_path).absolute()))
            hdlib = hydrodyn.HydroDynLib(get_library_path(module_name="hydrodyn"))
        except Exception as e:
            print(f"Failed to load library: {e}")
            sys.exit(1)

        # Configure library
        hdlib.InterpOrder = self.lib_config.interpolation_order
        hdlib.t_start = self.lib_config.time_start
        hdlib.dt = self.lib_config.time_interval
        hdlib.numTimeSteps = len(self.time)
        hdlib.gravity = self.lib_config.gravity
        hdlib.defWtrDens = self.lib_config.water_density
        hdlib.defWtrDpth = self.lib_config.water_depth
        hdlib.defMSL2SWL = self.lib_config.mean_sea_level_offset
        hdlib.numNodes = self.config.num_nodes

        # Initialize HydroDyn with input files
        # fh = open(Path(__file__).parent / seast_primary_file, "r")
        seastate_input = read_lines_from_file(self.config.seastate_primary_file)
        # fh = open(Path(__file__).parent / hd_primary_file, "r")
        hd_input = read_lines_from_file(self.config.hd_primary_file)
        try:
            hdlib.hydrodyn_init(seastate_input, hd_input)
        except Exception as e:
            print(f"Failed to initialize HydroDyn: {e}")
            sys.exit(1)

        # Store output channel information and initialize output arrays
        self.output_channel_names = hdlib.output_channel_names
        self.output_channel_units = hdlib.output_channel_units
        self.output_channel_values = np.zeros(hdlib.numChannels)
        self.all_output_channel_values = np.zeros((len(self.time), hdlib.numChannels + 1))

        return hdlib

    def run_simulation(self) -> None:
        """Run the main simulation loop."""
        # Initialize debug output if needed
        debug_output_file = None
        if self.config.debug_outputs:
            debug_output_file = hydrodyn.DriverDbg(
                self.config.debug_output_file,
                self.hdlib.numNodePts
            )

        try:
            # Process initial timestep
            self._process_timestep(
                0,
                self.time[0],
                debug_output_file
            )

            # Time stepping loop
            for i in range(len(self.time) - 1):
                # Correction loop
                for _ in range(self.config.num_corrections + 1):
                    self._process_timestep(
                        i + 1,
                        self.time[i + 1],
                        debug_output_file,
                        update_states=True,
                        previous_time=self.time[i]
                    )

        finally:
            # Close debug output if it was opened
            if debug_output_file:
                debug_output_file.end()

            # End HydroDyn simulation
            try:
                self.hdlib.hydrodyn_end()
            except Exception as e:
                print(f"Failed to end HydroDyn simulation: {e}")
                sys.exit(1)

        # Write output channels to file
        out_file = hydrodyn.WriteOutChans(
            self.config.output_file,
            self.hdlib.output_channel_names,
            self.hdlib.output_channel_units
        )
        out_file.write(self.all_output_channel_values)
        out_file.end()

    def _process_timestep(
        self,
        i_timestep: int,
        current_time: float,
        debug_output_file: Optional[hydrodyn.DriverDbg],
        update_states: bool = False,
        previous_time: Optional[float] = None
    ) -> None:
        """Process a single timestep in the simulation.

        Args:
            i_timestep: Current timestep index
            current_time: Current simulation time
            debug_output_file: Debug output handler
            update_states: Whether to update states
            previous_time: Previous timestep time (needed for state updates)
        """
        # Update node states from timeseries
        self.node_positions[0, 0:6] = self.timeseries[i_timestep, 1:7]
        self.node_velocities[0, 0:6] = self.timeseries[i_timestep, 7:13]
        self.node_accelerations[0, 0:6] = self.timeseries[i_timestep, 13:19]

        # Update states if requested
        if update_states:
            try:
                self.hdlib.hydrodyn_updateStates(
                    previous_time, current_time,
                    self.node_positions, self.node_velocities,
                    self.node_accelerations, self.node_forces_moments
                )
            except Exception as e:
                print(f"Failed to update states at T={current_time}: {e}")
                raise

            # Update node states again after state update
            self.node_positions[0, 0:6] = self.timeseries[i_timestep, 1:7]
            self.node_velocities[0, 0:6] = self.timeseries[i_timestep, 7:13]
            self.node_accelerations[0, 0:6] = self.timeseries[i_timestep, 13:19]

        # Calculate outputs
        try:
            self.hdlib.hydrodyn_calcOutput(
                current_time,
                self.node_positions, self.node_velocities, self.node_accelerations,
                self.node_forces_moments, self.output_channel_values
            )
        except Exception as e:
            print(f"Failed to calculate outputs at T={current_time}: {e}")
            raise

        # Write debug output if enabled
        if debug_output_file:
            debug_output_file.write(
                current_time,
                self.node_positions,
                self.node_velocities,
                self.node_accelerations,
                self.node_forces_moments
            )

        # Store outputs
        self.all_output_channel_values[i_timestep, :] = np.append(
            current_time,
            self.output_channel_values
        )

if __name__ == "__main__":
    driver = HydroDynDriver(HydroDynConfig(), LibraryConfig())
    driver.run_simulation()
