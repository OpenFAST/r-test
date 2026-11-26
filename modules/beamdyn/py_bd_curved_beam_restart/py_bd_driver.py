#-------------------------------------------------------------------------------
# LICENSING
#-------------------------------------------------------------------------------
# Copyright (C) 2026 National Renewable Energy Laboratory
#
# This file is part of BeamDyn
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
# Overview of BeamDyn python driver
#-------------------------------------------------------------------------------
# This script serves as a Python driver for the BeamDyn library. It demonstrates
# how to interact with the main subroutines of the BeamDyn C-bindings interface.
# It runs the case described by the BeamDyn driver input file (the same file the
# Fortran driver `beamdyn_driver` reads), so the results can be compared with the
# module test of the same case.
#
# NOTE: This script serves as a template and can be customized to meet
# individual requirements.
#
# Basic algorithm for using the BeamDyn Python library:
#   1. Initialize the Python wrapper library:
#      - Set necessary library values
#      - Set input file string arrays (from file/script)
#
#   2. Initialize the BeamDyn Fortran library (i.e. C-bindings interface)
#      - Set the initial root position, orientation, and velocity, and gravity
#      - Call bd_init once to initialize BeamDyn
#      - Handle any resulting errors
#
#   3. Timestep iteration:
#      - Set the root motion and loads at the next time
#      - Call bd_updateStates to propagate forward from t to t+dt
#      - Call bd_calcOutput. Handle any resulting errors
#      - Aggregate output channels
#
#   4. Restart (optional, see BeamDynConfig.checkpoint_time):
#      - Call bd_packStates to write a checkpoint file, then bd_end
#      - Call bd_init again with the same inputs, then bd_unpackStates
#      - Continue the timestep iteration
#
#   5. End:
#      - Call bd_end to close the BeamDyn library and free memory
#      - Handle any resulting errors

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
from pyOpenFAST import beamdyn

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
class BeamDynConfig:
    """Configuration settings for the BeamDyn simulation."""
    verbose: bool = False       # Enable verbose debug output

    #--------------------------------------
    # File names
    #--------------------------------------
    bd_driver_file: str = "bd_driver.inp"       # BeamDyn driver input file (same format as for beamdyn_driver)
    bd_output_file: str = "py_bd_driver.out"    # Output channels written by this script
    bd_root_name: str = "py_bd_driver"          # Root name for the BeamDyn summary and echo files

    #--------------------------------------
    # Restart
    #--------------------------------------
    # If set, the simulation is interrupted at this time (s): the states are written to a
    # checkpoint file (bd_packStates), the library is ended and initialized again, and the
    # states are restored (bd_unpackStates) before the simulation continues.  The results
    # must be the same as for an uninterrupted run.
    checkpoint_time: Optional[float] = 0.008
    checkpoint_root: str = "py_bd_driver"       # Checkpoint file is <checkpoint_root>.chkp

@dataclass
class LibraryConfig:
    """Configuration settings for the BeamDyn library."""
    interpolation_order: int = 1    # Order of interpolation (1: linear -- uses two time steps,
                                    # 2: quadratic -- uses three time steps)

@dataclass
class DriverInput:
    """Contents of a BeamDyn driver input file."""
    dynamic_solve: bool = True
    t_initial: float = 0.0
    t_final: float = 0.0
    dt: float = 0.0
    gravity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    root_position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    root_orientation: np.ndarray = field(default_factory=lambda: np.eye(3))
    root_angular_velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    distr_load: np.ndarray = field(default_factory=lambda: np.zeros(6))
    tip_load: np.ndarray = field(default_factory=lambda: np.zeros(6))
    primary_file: str = ""

def read_driver_input(file_name: str) -> DriverInput:
    """Read a BeamDyn driver input file (the input file of the Fortran driver)."""
    lines = read_lines_from_file(file_name)
    it = iter(lines)

    def skip(n):
        for _ in range(n):
            next(it)

    def number():
        return float(next(it).split()[0].replace("d", "e").replace("D", "e"))

    def logical():
        return next(it).split()[0].strip('."').lower().startswith("t")

    dvr = DriverInput()
    skip(3)                                             # header and section header
    dvr.dynamic_solve = logical()
    dvr.t_initial = number()
    dvr.t_final = number()
    dvr.dt = number()
    skip(1)                                             # gravity section header
    dvr.gravity = np.array([number() for _ in range(3)])
    skip(1)                                             # frame section header
    dvr.root_position = np.array([number() for _ in range(3)])
    skip(2)                                             # DCM comment lines
    dvr.root_orientation = np.array([[float(v) for v in next(it).split()[:3]] for _ in range(3)])
    if not logical():
        sys.exit("GlbRotBladeT0 = False is not supported by this driver")
    skip(1)                                             # root velocity section header
    dvr.root_angular_velocity = np.array([number() for _ in range(3)])
    skip(1)                                             # applied force section header
    dvr.distr_load = np.array([number() for _ in range(6)])
    dvr.tip_load = np.array([number() for _ in range(6)])
    if int(number()) > 0:
        sys.exit("The multi-point load table (NumPointLoads > 0) is not supported by this driver")
    skip(3)                                             # point load table header, primary file section header
    dvr.primary_file = next(it).split()[0].strip('"\'')
    return dvr

def rotation_matrix(axis: np.ndarray, angle: float) -> np.ndarray:
    """Rotation matrix for a rotation of `angle` about the unit vector `axis` (Rodrigues formula)."""
    K = np.array([[0.0, -axis[2], axis[1]], [axis[2], 0.0, -axis[0]], [-axis[1], axis[0], 0.0]])
    return np.eye(3) + np.sin(angle) * K + (1.0 - np.cos(angle)) * (K @ K)

#-------------------------------------------------------------------------------
# Main driver class
#-------------------------------------------------------------------------------
class BeamDynDriver:
    """Main driver class for the BeamDyn simulation."""

    def __init__(self, config: BeamDynConfig, lib_config: LibraryConfig):
        """Initialize the BeamDyn driver."""
        self.config = config
        self.lib_config = lib_config

        # Read the driver input file and set time parameters.  The Fortran driver takes
        # INT((t_final - t_initial)/dt) + 1 steps (a static solve stops after 9 load steps).
        self.dvr = read_driver_input(self.config.bd_driver_file)
        self.dt = self.dvr.dt
        num_steps = int((self.dvr.t_final - self.dvr.t_initial) / self.dt) + 1
        if not self.dvr.dynamic_solve:
            num_steps = min(num_steps, 9)
        self.time = self.dvr.t_initial + self.dt * np.arange(num_steps + 1)

        # Initialize library
        self.bdlib = self._initialize_library()

    def _root_motion(self, t: float):
        """Root motion at time t: the root rotates about the global origin at a constant angular velocity,
        as in the BeamDyn Fortran driver.  Returns displacement (3), DCM (3,3), velocity (6), acceleration (6)."""
        omega = self.dvr.root_angular_velocity
        w = np.linalg.norm(omega)
        r0 = self.dvr.root_position
        R = rotation_matrix(omega / w, w * (t - self.dvr.t_initial)) if w > 0.0 else np.eye(3)
        p = R @ r0                                                  # rotated root position
        displacement = p - r0
        orientation = self.dvr.root_orientation @ R.T               # the root frame rotates with the body
        velocity = np.concatenate([np.cross(omega, p), omega])
        acceleration = np.concatenate([np.cross(omega, np.cross(omega, p)), np.zeros(3)])
        return displacement, orientation, velocity, acceleration

    def _set_inputs(self, t: float) -> None:
        """Set the root motion and the loads at time t."""
        self.bdlib.bd_setRootMotion(*self._root_motion(t))
        self.bdlib.bd_setPointLoads(self.point_loads)
        self.bdlib.bd_setDistrLoads(self.distr_loads)

    def _initialize_library(self) -> beamdyn.BeamDynLib:
        """Initialize the BeamDyn library."""
        try:
            bdlib = beamdyn.BeamDynLib(get_library_path(module_name="beamdyn"))
        except Exception as e:
            print(f"Cannot load BeamDyn library: {e}")
            sys.exit(1)

        # Load the primary input file.  Its contents are passed to the library; the blade
        # file named in it is read by BeamDyn from the working directory.
        bd_input_string_array = read_lines_from_file(self.dvr.primary_file)

        # Initial root velocity for a root rotating about the global origin
        omega = self.dvr.root_angular_velocity
        root_velocity = np.concatenate([np.cross(omega, self.dvr.root_position), omega])

        # Initialize BeamDyn
        try:
            bdlib.bd_init(
                1,
                bd_input_string_array,
                self.config.bd_root_name,
                self.dvr.root_position,
                self.dvr.root_orientation,
                root_velocity,
                self.dvr.gravity,
                self.dt,
                interp_order=self.lib_config.interpolation_order,
                dynamic_solve=self.dvr.dynamic_solve,
                write_outputs=False,
            )
        except Exception as e:
            print(f"BeamDyn initialization failed: {e}")
            sys.exit(1)

        # Reference positions of the output and load nodes
        out_pos, _, pl_pos, _ = bdlib.bd_getRefPositions()
        if self.config.verbose:
            print(f"Output nodes: {bdlib.num_output_nodes}, point load nodes: {bdlib.num_point_load_nodes}, "
                  f"distributed load nodes: {bdlib.num_distr_load_nodes}")

        # Loads: constant distributed load on every distributed load node and a constant
        # load at the tip (the last point load node, as in the Fortran driver)
        self.distr_loads = np.tile(self.dvr.distr_load, (bdlib.num_distr_load_nodes, 1))
        self.point_loads = np.zeros((bdlib.num_point_load_nodes, 6))
        self.point_loads[-1, :] = self.dvr.tip_load

        # Set up the output channels listed in the BD input file (kept when the library is initialized again for a restart)
        if not hasattr(self, "output_channel_array"):
            self.output_channel_names = bdlib.output_channel_names
            self.output_channel_units = bdlib.output_channel_units
            self.output_channel_values = np.zeros(len(self.output_channel_names))
            self.output_channel_array = np.zeros((len(self.time), len(self.output_channel_names) + 1)) # includes time

        return bdlib

    def run_simulation(self) -> None:
        """Run the main simulation loop."""
        try:
            # Inputs and outputs at the initial time (required before the first bd_updateStates)
            self._set_inputs(self.time[0])
            self._calc_output(0)

            # Time stepping loop
            for i in range(len(self.time) - 1):
                # Print progress
                if (i % max(1, round(1.0/self.dt))) == 0:
                    print(f"Time: {self.time[i]}")

                # Checkpoint and restart at the requested time
                if self.config.checkpoint_time is not None and \
                   abs(self.time[i] - self.config.checkpoint_time) < 0.5 * self.dt:
                    self._restart(self.time[i])

                # Inputs at the next time, update the states, calculate the outputs
                self._set_inputs(self.time[i + 1])
                self.bdlib.bd_updateStates(self.time[i], self.time[i + 1])
                self._calc_output(i + 1)

        finally:
            # End BeamDyn simulation
            try:
                self.bdlib.bd_end()
            except Exception as e:
                print(f"Failed to end BeamDyn simulation: {e}")
                sys.exit(1)

        # Write output channels to file
        out_file = beamdyn.WriteOutChans(
            self.config.bd_output_file,
            self.output_channel_names,
            self.output_channel_units
        )
        out_file.write(self.output_channel_array)
        out_file.end()

    def _restart(self, t: float) -> None:
        """Write a checkpoint, end the library, initialize it again, and restore the checkpoint."""
        print(f"Time: {t} -- writing checkpoint {self.config.checkpoint_root}.chkp and restarting from it")
        self.bdlib.bd_packStates(self.config.checkpoint_root)
        self.bdlib.bd_end()
        self.bdlib = self._initialize_library()
        self.bdlib.bd_unpackStates(self.config.checkpoint_root)

    def _calc_output(self, i_timestep: int) -> None:
        """Calculate and store the outputs at one time step."""
        try:
            self.bdlib.bd_calcOutput(self.time[i_timestep], self.output_channel_values)
        except Exception as e:
            print(f"Failed to calculate outputs at T={self.time[i_timestep]}: {e}")
            raise

        self.output_channel_array[i_timestep, :] = np.append(self.time[i_timestep], self.output_channel_values)

if __name__ == "__main__":
    driver = BeamDynDriver(BeamDynConfig(), LibraryConfig())
    driver.run_simulation()
