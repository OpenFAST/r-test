#-------------------------------------------------------------------------------
# LICENSING
#-------------------------------------------------------------------------------
# Copyright (C) 2021-present by National Renewable Energy Lab (NREL)
#
# This file is part of MoorDyn
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
# Overview of MoorDyn python driver
#-------------------------------------------------------------------------------
# This script serves as a Python driver for the MoorDyn library. It demonstrates
# how to interact with the main subroutines of MoorDyn.
#
# NOTE: This script serves as a template and can be customized to meet
# individual requirements.
#
# Basic algorithm for using MoorDyn Python library:
#   1. Initialize the Python wrapper library:
#      - Set necessary library values
#      - Set input file string arrays (from file/script)
#
#   2. Initialize the MoorDyn Fortran library (i.e. C-bindings interface)
#      - Set initial position, velocity, and acceleration values
#      - Call moordyn_init once to initialize MoorDyn
#      - Handle any resulting errors
#
#   3. Timestep iteration:
#      - Set extrapolated values for inputs
#      - Call moordyn_updatestates to propagate forward from t to t+dt
#      - Set position, velocity, and acceleration information for all nodes
#      - Call moordyn_calcoutput. Handle any resulting errors
#      - Return the resulting force and moment array
#      - Aggregate output channels
#
#   4. End:
#      - Call moordyn_end to close the MoorDyn library and free memory
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
from OpynFAST import moordyn

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
# Configuration classes
#-------------------------------------------------------------------------------
@dataclass
class MoorDynConfig:
    """Configuration settings for MoorDyn simulation."""
    num_corrections: int = 0    # Number of correction steps to perform
    verbose: bool = False       # Enable verbose debug output

    #--------------------------------------
    # File names
    #--------------------------------------
    md_input_file: str = "md_primary.inp"
    md_output_file: str = "MD.out"
    md_test_file: str = "5MW_OC4Semi_WSt_WavesWN.out"
    debug_output_file: str = "MD.dbg"

@dataclass
class LibraryConfig:
    """Configuration settings for MoorDyn library."""
    interpolation_order: int = 2    # Order of interpolation (1: linear -- uses two time steps,
                                    # 2: quadratic -- uses three time steps)
    gravity: float = 9.80665        # Gravity (m/s^2)
    water_density: float = 1025.    # Water density (kg/m^3)
    water_depth: float = 200.       # Water depth (m), depth is positive

#-------------------------------------------------------------------------------
# Main driver class
#-------------------------------------------------------------------------------
class MoorDynDriver:
    """Main driver class for MoorDyn simulation."""

    def __init__(self, config: MoorDynConfig, lib_config: LibraryConfig):
        """Initialize the MoorDyn driver."""
        self.config = config
        self.lib_config = lib_config

        # Load test data and set time parameters
        self.test_data = self._load_test_data()
        self.time = self.test_data[:, 0]
        self.dt = self.time[1] - self.time[0]

        # Initialize library
        self.mdlib = self._initialize_library()

        # Initialize debug output if needed
        self.debug_output = None
        if self.config.verbose:
            self.debug_output = moordyn.DriverDbg(self.config.debug_output_file)

    def _load_test_data(self) -> np.ndarray:
        """Load test data from file."""
        try:
            with open(self.config.md_test_file, "r") as ft:
                lines = ft.read().splitlines()[8:-1]  # Skip header rows and last line
                data = np.array([list(map(float, line.split())) for line in lines])
                return data

        except Exception as e:
            print(f"Cannot load MoorDyn test file: {e}")
            sys.exit(1)

    def _initialize_library(self) -> moordyn.MoorDynLib:
        """Initialize the MoorDyn library."""
        try:
            mdlib = moordyn.MoorDynLib(get_library_path(module_name="moordyn"))
        except Exception as e:
            print(f"Cannot load MoorDyn library: {e}")
            sys.exit(1)

        # Set library parameters
        mdlib.dt = self.dt # time interval
        mdlib.total_time = self.time[-1] # total or end time
        mdlib.numTimeSteps = len(self.time) # number of time steps

        # Load and process input file
        md_input_string_array = read_lines_from_file(self.config.md_input_file)

        # Extract initial conditions from test data
        #
        # Initial position of platform/hull/substructure in OpenFAST global coordinates
        # Format: [x, y, z, Rx, Ry, Rz] where units are [m, m, m, rad, rad, rad]
        self.platform_init_pos = self.test_data[0, 1:7]
        # Initial velocities of platform/hull/substructure
        # Format: [x_dot, y_dot, z_dot, Rx_dot, Ry_dot, Rz_dot] where
        # _dot denotes first derivatives (velocities)
        self.platform_init_vel = self.test_data[0, 7:13]
        # Initial accelerations of platform/hull/substructure
        # Format: [x_ddot, y_ddot, z_ddot, Rx_ddot, Ry_ddot, Rz_ddot] where
        # _ddot denotes second derivatives (accelerations)
        self.platform_init_acc = self.test_data[0, 13:19]

        # Initialize MoorDyn
        try:
            mdlib.md_init(
                md_input_string_array,
                self.lib_config.gravity,
                self.lib_config.water_density,
                self.lib_config.water_depth,
                self.platform_init_pos,
                self.lib_config.interpolation_order
            )
        except Exception as e:
            print(f"MoorDyn initialization failed: {e}")
            sys.exit(1)

        # Set up the output channels listed in the MD input file
        self.output_channel_names = mdlib._channel_names.value
        print("output_channel_names: ", self.output_channel_names)
        self.output_channel_units = mdlib._channel_units.value
        print("output_channel_units: ", self.output_channel_units)
        self.output_channel_values = np.zeros(mdlib._numChannels.value)
        self.output_channel_array = np.zeros((mdlib.numTimeSteps, mdlib._numChannels.value + 1)) # includes time

        return mdlib

    def run_simulation(self) -> None:
        """Run the main simulation loop."""
        # Initialize arrays for outputs
        forces = np.zeros(6)

        try:
            # Process initial timestep
            self._process_timestep(
                0,
                self.time[0],
                self.platform_init_pos,   # positions
                self.platform_init_vel,   # velocities
                self.platform_init_acc,   # accelerations
                forces,
                update_states=False,
                previous_time=None
            )

            # Time stepping loop
            for i in range(len(self.time) - 1):
                # Print progress
                if (i % round(1.0/self.dt)) == 0:
                    print(f"Time: {self.time[i]}")

                # Get current state from test data
                positions = self.test_data[i + 1, 1:7]
                velocities = self.test_data[i + 1, 7:13]
                accelerations = self.test_data[i + 1, 13:19]

                # Correction loop
                for _ in range(self.config.num_corrections + 1):
                    self._process_timestep(
                        i + 1,
                        self.time[i + 1],
                        positions,
                        velocities,
                        accelerations,
                        forces,
                        update_states=True,
                        previous_time=self.time[i]
                    )

        finally:
            # End MoorDyn simulation
            try:
                self.mdlib.md_end()
            except Exception as e:
                print(f"Failed to end MoorDyn simulation: {e}")
                sys.exit(1)

            if self.debug_output:
                self.debug_output.end()

        # Write output channels to file
        channel_names = self.output_channel_names.decode().split()
        channel_units = self.output_channel_units.decode().split()
        print("channel_names: ", channel_names)
        print("channel_units: ", channel_units)
        out_file = moordyn.WriteOutChans(
            self.config.md_output_file,
            channel_names,
            channel_units
        )
        out_file.write(self.output_channel_array)
        out_file.end()

    def _process_timestep(
        self,
        i_timestep: int,
        current_time: float,
        positions: np.ndarray,
        velocities: np.ndarray,
        accelerations: np.ndarray,
        forces: np.ndarray,
        update_states: bool = False,
        previous_time: Optional[float] = None
    ) -> None:
        """Process a single timestep in the simulation."""
        # Update states if requested
        if update_states:
            try:
                self.mdlib.md_updateStates(
                    previous_time,
                    current_time,
                    positions,
                    velocities,
                    accelerations
                )
            except Exception as e:
                print(f"Failed to update states at T={current_time}: {e}")
                raise

        # Calculate outputs
        try:
            self.mdlib.md_calcOutput(
                current_time,
                positions,
                velocities,
                accelerations,
                forces,
                self.output_channel_values
            )
        except Exception as e:
            print(f"Failed to calculate outputs at T={current_time}: {e}")
            raise

        # Store outputs
        self.output_channel_array[i_timestep, :] = np.append(current_time, self.output_channel_values)

        # Write debug output if enabled
        if self.config.verbose:
            self.debug_output.write(current_time, positions, velocities, accelerations, forces)

if __name__ == "__main__":
    driver = MoorDynDriver(MoorDynConfig(), LibraryConfig())
    driver.run_simulation()
