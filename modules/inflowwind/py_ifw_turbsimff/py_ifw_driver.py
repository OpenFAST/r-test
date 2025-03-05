#-------------------------------------------------------------------------------
# LICENSING
#-------------------------------------------------------------------------------
# Copyright (C) 2021-present by National Renewable Energy Lab (NREL)
#
# This file is part of InflowWind
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
# Overview of InflowWind python driver
#-------------------------------------------------------------------------------
# This script serves as a Python driver for the InflowWind library. It demonstrates
# how to interact with the main subroutines of InflowWind.
#
# NOTE: This script serves as a template and can be customized to meet
# individual requirements.
#
# Basic algorithm for using InflowWind python library:
#   1. Initialize the Python wrapper library:
#      - Set necessary library values (e.g., numWindPts, dt, numTimeSteps)
#      - Load input file data (from file/script)
#   2. Initialize the InflowWind Fortran library:
#      - Call ifw_init once
#      - Handle any resulting errors
#   3. Timestep Iterations:
#      - Set array of positions
#      - Call ifw_calcoutput and handle errors
#      - Return resulting velocities array
#      - Aggregate output channels
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

import numpy as np

# Path to find the inflowwind_library.py from the local directory
#
# NOTE: This file handles the conversion from python to c-bound types
#       and should NOT be changed by the user
os.chdir(Path(__file__).parent)
ifw_lib_path = Path(__file__).parent.joinpath(*[".."]*5, "modules", "inflowwind", "python-lib")
sys.path.insert(0, str(ifw_lib_path))
print(f"Importing 'inflowwind_library' from {ifw_lib_path}")
import inflowwind_library as ifw

#-------------------------------------------------------------------------------
# Configuration classes containing problem inputs
#-------------------------------------------------------------------------------
@dataclass
class InflowWindConfig:
    """Configuration settings for InflowWind simulation."""
    # Time settings
    #
    # For this test case, we are checking between 30 and 30.8 seconds.  The
    # inflowwind python library interface must be informed about the
    # following 2 time related information variables
    #   - ifwlib.dt -> timestep inflowwind is called at
    #   - ifwlib.numTimeSteps -> total number of timesteps, used to construct
    #     arrays to hold the output channel
    t_start: float = 30.    # initial time
    t_final: float = 30.8   # final time
    dt: float = 0.1         # time interval that ifw is being called at

    # Debug settings
    debug_level: int = 3  # 0-4

    # File paths
    #
    # Primary input: This is identical to what InflowWind would read from disk if we were not
    # passing it. When coupled to other codes, this may be passed directly from memory (i.e.
    # during optimization with WEIS), or read as a template and edited in memory for each
    # iteration loop.
    primary_ifw_file: str = "ifw_primary.inp"

    # Position input: Contains an array of points (Nx3 [X,Y,Z] values) that will be passed to
    # InflowWind at each timestep. When coupled to other codes, these positions would be passed
    # directly from the structural code instead of reading from a file.
    position_file: str = "Points.inp"

    # Velocities output: For testing/debugging, the calculated velocities at each position point
    # are written to this file. When coupled to other codes, these velocities would be returned
    # directly to the calling code instead of writing to file.
    velocities_file: str = "Points.Velocity.dat"

    # Output channels: Contains the aggregated output channels requested in the outlist section.
    # When coupled to other codes, these values could be passed back for writing by the calling
    # code instead of writing directly to file here.
    output_file: str = "ifw_primary.out"

#-------------------------------------------------------------------------------
# Helper functions
#-------------------------------------------------------------------------------
def read_lines_from_file(file_path: str) -> List[str]:
    """Reads a file line by line, stripping whitespace.

    Args:
        file_path: Path to the file to read

    Returns:
        List of stripped lines from the file
    """
    with open(file_path, "r") as fh:
        return [line.rstrip() for line in fh]

def read_positions_from_file(file_path: str) -> np.ndarray:
    """Reads initial position of points from a file.

    The file should contain a list of X,Y,Z coordinates in the OpenFAST global/inertial
    coordinate system, with one point per line. Lines starting with '#' are treated as
    comments and ignored. Each line should contain exactly 3 space-separated floating
    point values representing the X, Y, and Z coordinates respectively.

    Example format:
        #  x     y     z
        0.0  0.0  150.0
        0.0  0.0  125.0
        0.0  0.0  175.0
        0.0  25.0 150.0
        0.0 -25.0 150.0

    Args:
        file_path: Path to the positions file

    Returns:
        numpy.ndarray: Array of position points (Nx3) where N is the number of points
        and each point has [X,Y,Z] coordinates

    Raises:
        ValueError: If positions file format is invalid (doesn't contain exactly 3 values per line)
    """
    positions = []
    with open(file_path, "r") as fh:
        for line in fh:
            if not line.startswith('#'):
                positions.append([float(i) for i in line.split()])

    positions = np.asarray(positions)
    if positions.shape[1] != 3:
        raise ValueError("Error in parsing points file. Does not contain a Nx3 set of position points")

    return positions

def get_library_path() -> str:
    """Determines the correct library path based on platform.

    Returns:
        str: Path to the InflowWind library for the current platform

    Raises:
        SystemExit: If library cannot be found
    """
    basename = "libifw_c_binding"
    build_path = Path("..").joinpath(*[".."] * 4, "build")

    if sys.platform in ["linux", "linux2"]:
        return str(build_path / "modules" / "inflowwind" / f"{basename}.so")

    if sys.platform == "darwin":
        return str(build_path / "modules" / "inflowwind" / f"{basename}.dylib")

    if sys.platform == "win32":
        # Try CMake location first
        dll_path = build_path / "modules" / "inflowwind" / f"{basename}.dll"
        if dll_path.is_file():
            return str(dll_path)

        # Try VS build location if CMake location not found
        bit_version = "Win32" if not sys.maxsize > 2**32 else "x64"
        vs_path = build_path / "bin" / f"InflowWind_c_binding_{bit_version}.dll"

        if not vs_path.is_file():
            print(f"Python is {bit_version} and cannot find {bit_version} InflowWind DLL")
            sys.exit(1)
        return str(vs_path)

#-------------------------------------------------------------------------------
# Main driver class
#-------------------------------------------------------------------------------
class InflowWindDriver:
    """Main driver class for InflowWind simulation."""

    def __init__(self, config: InflowWindConfig):
        """Initialize the InflowWind driver.

        Args:
            config: Configuration settings for the simulation
        """
        self.config = config

        # Initialize data structures
        self.positions = read_positions_from_file(self.config.position_file)
        self.velocities = np.zeros((self.positions.shape[0], 3))
        self.time = np.linspace(
            self.config.t_start,
            self.config.t_final,
            int((self.config.t_final - self.config.t_start) / self.config.dt) + 1 # 9
        )

        # Initialize library
        self.ifwlib = self._initialize_library()

    def _initialize_library(self) -> ifw.InflowWindLib:
        """Initialize the InflowWind library with configuration settings.

        Returns:
            Configured instance of the InflowWind library

        Raises:
            SystemExit: If library initialization fails
        """
        try:
            ifwlib = ifw.InflowWindLib(get_library_path())
        except Exception as e:
            print(f"Failed to load library: {e}")
            sys.exit(1)

        # Configure library
        #
        # ifwlib.dt -> timestep inflowwind is called at
        ifwlib.dt = self.config.dt
        # ifwlib.numTimeSteps -> total number of timesteps, used to construct arrays to hold the output channel
        ifwlib.numTimeSteps = len(self.time)
        # ifwlib.numWindPts -> total number of wind points requesting velocities for at each time step
        ifwlib.numWindPts = self.positions.shape[0]
        # ifwlib.debuglevel -> debug level for IfW library
        ifwlib.debuglevel = self.config.debug_level

        return ifwlib

    def run_simulation(self) -> None:
        """Run the main simulation loop."""
        # Initialize output arrays
        output_channel_values = None
        all_output_channel_values = None

        # Read input file
        ifw_input = read_lines_from_file(self.config.primary_ifw_file)

        # Initialize debug output if needed
        debug_output = ifw.DebugOut(
            self.config.velocities_file,
            self.ifwlib.numWindPts
        )

        try:
            # Initialize InflowWind -> only need to call it once
            self.ifwlib.ifw_init(ifw_input)

            # Initialize output arrays
            output_channel_values = np.zeros(self.ifwlib.numChannels)
            all_output_channel_values = np.zeros((len(self.time), self.ifwlib.numChannels + 1))


            # Time stepping loop: step through all the timesteps
            #   1. Set the positions array with node positions from the structural solver
            #   2. Call ifw_calc_output to retrieve the corresponding velocities
            #      to pass back to the calling code (or write to disk in this example)
            for i, t in enumerate(self.time):
                # NOTE: When coupled to another code, set the positions info for this
                # timestep here in the calling algorithm. For this regression test example,
                # the positions are kept constant throughout the simulation.

                try:
                    self.ifwlib.ifw_calc_output(
                        t,
                        self.positions,
                        self.velocities,
                        output_channel_values
                    )
                except Exception as e:
                    print(f"Error in calculation at t={t}: {e}")
                    raise

                # NOTE: When coupled to a different code, this is where the velocity info
                # would be passed to the aerodynamic solver

                # Write debug output (positions and velocities) for each timestep.
                # This is primarily used for regression testing, writing one row
                # for each timestep + position array entry.
                debug_output.write(t, self.positions, self.velocities)

                # Store the channel outputs requested in the InflowWind input file's OutList section.
                # In OpenFAST, these would be added to the output channel array for all modules.
                # Here we store them with the timestamp for writing to file at the end of simulation.
                all_output_channel_values[i,:] = np.append(t, output_channel_values)

        finally:
            # Close the debug output file
            debug_output.end()

            # Call ifw_end to clean up resources
            # NOTE: ifw_end is automatically called during error handling of ifw_init and
            # ifw_calc_output. While this works for InflowWind, other modules might need
            # to retrieve data from memory before cleanup.
            self.ifwlib.ifw_end()

        # Write final outputs
        out_file = ifw.WriteOutChans(
            self.config.output_file,
            self.ifwlib.output_channel_names,
            self.ifwlib.output_channel_units
        )
        out_file.write(all_output_channel_values)
        out_file.end()

        print("InflowWind completed successfully")

if __name__ == "__main__":
    driver = InflowWindDriver(InflowWindConfig())
    driver.run_simulation()
