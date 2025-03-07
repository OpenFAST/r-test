#-------------------------------------------------------------------------------
# LICENSING
#-------------------------------------------------------------------------------
# Copyright (C) 2021-present by National Renewable Energy Lab (NREL)
#
# This file is part of AeroDyn
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
# Overview of AeroDyn x InflowWind python driver
#-------------------------------------------------------------------------------
# This script serves as a Python driver for the AeroDyn library with InflowWind
# integration. It demonstrates how to interact with the main subroutines of
# AeroDyn.
#
# NOTE: This script serves as a template and can be customized to meet
# individual requirements.
#
# Workflow for using the AeroDyn x InflowWind Python library:
#   1. Initialize the Python Wrapper:
#      - Set necessary library parameters (e.g., number of turbines, simulation
#        time)
#      - Load input file data (from file/script)
#
#   2. Initialize the AeroDyn Fortran Library (C-bindings interface):
#      - ADI_PreInit: Specify the number of turbines
#      - ADI_SetupTurb: Initialize each rotor and iterate over turbines
#      - ADI_Init: Initialize the simulation environment by calling ADI
#
#   3. Perform Timestep Iterations:
#      - ADI_SetRotorMotion: Define the motion parameters for each turbine and iterate
#        over turbines
#      - ADI_UpdateStates: Advance the simulation to the next timestep
#      - ADI_CalcOutput: Retrieve simulation outputs
#      - ADI_GetRotorLoads: Obtain load data for each rotor and iterate over
#        turbines
#
#   4. Finalize the Simulation:
#      - Call adi_end to properly close the AeroDyn library and release resources
#      - Handle any errors that may have occurred during the process

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np

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

# Path to find the aerodyn_inflow_library.py from the local directory
#
# NOTE: This file handles the conversion from python to C-bound types
# and should NOT be modified by the user
os.chdir(Path(__file__).parent)
adi_lib_path = Path(__file__).parent.joinpath(*[".."]*5, "modules", "aerodyn", "python-lib")
sys.path.insert(0, str(adi_lib_path))
print(f"Importing 'aerodyn_inflow_library' from {adi_lib_path}")
import aerodyn_inflow_library as adi

#-------------------------------------------------------------------------------
# Configuration classes containing problem inputs
#-------------------------------------------------------------------------------
@dataclass
class AeroDynConfig:
    """Configuration settings for AeroDyn simulation."""
    num_turbines: int = 1          # Number of turbines
    is_hawt: int = 1               # 1: HAWT, 0: VAWT or cross-flow
    num_blades: int = 3            # Number of blades
    vtk_field_len: int = 5         # Length of the time field in filename
    time_steps_to_run: int = 4     # Number of time steps to run
    num_corrections: int = 0       # Number of corrections to perform
    debug_outputs: int = 1         # For checking the interface, set this to 1

    #--------------------------------------
    # File names
    #--------------------------------------
    vtk_dir: str = "vtkRef"
    # Primary input files: This is identical to what AeroDyn would read from disk
    # if we were not passing it. When coupled to other codes, this may be passed
    # directly from memory (e.g. during optimization with WEIS), or read as a
    # template and edited in memory for each iteration loop.
    primary_ad_file: str = "ad_primary.dat"
    primary_ifw_file: str = "ifw_primary.dat"
    # Debug output file: When coupled into another code, an array of position/orientation,
    # velocities, and accelerations are passed in, and an array of Forces + Moments is
    # returned. For debugging, it may be useful to dump all off this to a file.
    debug_output_file: str = "DbgOutputs.out"
    # Output file: When coupled to another code, the channels requested in the outlist
    # section of the output file are passed back for writing to file. Here we will
    # write the aggregated output channels to a file at the end of the simulation.
    output_file: str = "py_ad_driver.out"

    # Mesh root names
    hub_mesh_root: str = "5MW_OC4Semi_WSt_WavesWN.AD_HubMotion"
    nac_mesh_root: str = "5MW_OC4Semi_WSt_WavesWN.ED_Nacelle"
    bld_root_mesh_root: str = "5MW_OC4Semi_WSt_WavesWN.AD_BladeRootMotion"
    bld_mesh_root: str = "5MW_OC4Semi_WSt_WavesWN.ED_BladeLn2Mesh_motion"

@dataclass
class LibraryConfig:
    """Configuration settings for AeroDyn library."""
    interpolation_order: int = 2                # Order of the interpolation
    time_interval: float = 0.0125               # Time interval for ADI calls
    gravity: float = 9.80665                    # Gravitational acceleration (m/s^2)
    density: float = 1.225                      # Air density (kg/m^3)
    kinematic_viscosity: float = 1.464E-05      # Kinematic viscosity of working fluid (m^2/s)
    speed_of_sound: float = 335.                # Speed of sound in working fluid (m/s)
    atmospheric_pressure: float = 103500.       # Atmospheric pressure (Pa) [used only for an MHK turbine cavitation check]
    vapor_pressure: float = 1700.               # Vapor pressure of working fluid (Pa) [used only for an MHK turbine cavitation check]
    water_depth: float = 0.                     # Water depth (m)
    mean_sea_level_offset: float = 0.           # Offset between still-water level and mean sea level (m) [positive upward]
    store_horizontal_hub_velocity: bool = False # Store horizontal hub velocity
    write_vtk: int = 2                          # Animation
    write_vtk_type: int = 3                     # Surface and line meshes
    debug_level: int = 0                        # 0-4
    transpose_dcm: int = 1                      # 0=false, 1=true

    @property
    def write_vtk_dt(self) -> float:
        return self.time_interval * 4.          # Write for every 4th timestep

#-------------------------------------------------------------------------------
# Main driver class
#-------------------------------------------------------------------------------
class AeroDynDriver:
    """Main driver class for AeroDyn simulation.

    This class manages the initialization and execution of the AeroDyn simulation.
    It handles the configuration of the simulation parameters, the initialization
    of the AeroDyn library, and the execution of the main simulation loop.
    """

    def __init__(self, config: AeroDynConfig, lib_config: LibraryConfig):
        self.config = config
        self.lib_config = lib_config

        # Initialize mesh data structures
        self._initialize_mesh_data()

        # Initialize library
        self.adilib = self._initialize_library()

        # Initialize output arrays as placeholders
        self.output_channel_values = None
        self.all_output_channel_values = None
        self.disk_avg_vel = None

    def _initialize_mesh_data(self) -> None:
        """Initializes mesh data from VTK files for hub, nacelle, and blades.

        Reads initial positions and orientations from VTK reference files and stores
        them as class attributes for later use in the simulation.
        """
        # Initialize hub and nacelle positions
        read_vtk_ref = lambda root_name: read_reference_positions_from_vtk(
            os.path.sep.join([self.config.vtk_dir, root_name + "_Reference.vtp"])
        )
        self.init_hub_pos, self.init_hub_orient, num_pts = read_vtk_ref(
            self.config.hub_mesh_root
        )
        self.init_nacelle_pos, self.init_nacelle_orient, num_pts = read_vtk_ref(
            self.config.nac_mesh_root
        )

        # Initialize blade root positions and orientations
        self.init_root_pos = np.zeros((self.config.num_blades, 3), dtype="float32")
        self.init_root_orient = np.zeros((self.config.num_blades, 9), dtype="float64")
        for i in range(self.config.num_blades):
            self.init_root_pos[i,:], self.init_root_orient[i,:], num_pts = read_vtk_ref(
                self.config.bld_root_mesh_root + str(i+1)
            )

        # Initialize blade mesh positions and orientations
        self.num_blade_node = np.zeros((self.config.num_blades), dtype=int)
        self.init_mesh_pos = np.empty((0, 3), dtype="float32")
        self.init_mesh_orient = np.empty((0, 9), dtype="float64")
        self.init_mesh_pt_to_blade_num = np.empty((0), dtype=int)

        for i in range(self.config.num_blades):
            tmp_pos, tmp_orient, num_pts = read_vtk_ref(
                self.config.bld_mesh_root + str(i+1)
            )
            self.init_mesh_pos = np.concatenate((self.init_mesh_pos, tmp_pos))
            self.init_mesh_orient = np.concatenate((self.init_mesh_orient, tmp_orient))
            self.num_blade_node[i] = num_pts

            # Store blade number for these points
            tmp_pt_to_blade_num = np.full(num_pts, i+1, dtype=int)
            self.init_mesh_pt_to_blade_num = np.concatenate(
                (self.init_mesh_pt_to_blade_num, tmp_pt_to_blade_num)
            )

    def _initialize_library(self) -> adi.AeroDynInflowLib:
        """Initializes the AeroDyn library with configuration settings.

        Returns:
            AeroDynInflowLib: Configured instance of the AeroDyn library.

        Raises:
            SystemExit: If library initialization fails.
        """
        library_path = get_library_path(module_name="aerodyn")
        try:
            adilib = adi.AeroDynInflowLib(library_path)
        except Exception as e:
            print(f"Failed to load AeroDyn library at {library_path}: {e}")
            sys.exit(1)

        #--------------------------------------
        # Configure library
        #--------------------------------------
        adilib.InterpOrder   = self.lib_config.interpolation_order

        # Time settings
        adilib.dt            = self.lib_config.time_interval
        adilib.numTimeSteps  = self.config.time_steps_to_run

        # Physical parameters
        adilib.gravity       = self.lib_config.gravity
        adilib.defFldDens    = self.lib_config.density
        adilib.defKinVisc    = self.lib_config.kinematic_viscosity
        adilib.defSpdSound   = self.lib_config.speed_of_sound
        adilib.defPatm       = self.lib_config.atmospheric_pressure
        adilib.defPvap       = self.lib_config.vapor_pressure
        adilib.WtrDpth       = self.lib_config.water_depth
        adilib.MSL2SWL       = self.lib_config.mean_sea_level_offset
        adilib.numTurbines   = self.config.num_turbines

        # Visualization settings
        adilib.storeHHvel    = self.lib_config.store_horizontal_hub_velocity
        adilib.WrVTK         = self.lib_config.write_vtk
        adilib.WrVTK_Type    = self.lib_config.write_vtk_type
        adilib.WrVTK_DT      = self.lib_config.write_vtk_dt
        adilib.transposeDCM  = self.lib_config.transpose_dcm

        # Debugging of internals of ADI library
        adilib.debuglevel    = self.lib_config.debug_level

        return adilib

    def run_simulation(self) -> None:
        """Run the main simulation loop with corrections."""
        self._initialize_simulation()

        # Initialize debug output file if needed
        debug_output_file = None
        if self.config.debug_outputs:
            debug_output_file = adi.DriverDbg(
                self.config.debug_output_file, self.adilib.numMeshPts
            )

        try:
            # Time stepping loop with corrections
            print(f"Time steps: {self.adilib.numTimeSteps}")
            for i in range(0, self.adilib.numTimeSteps + 1):
                current_time = i * self.adilib.dt
                print(f"Time step: {i} at {current_time}")

                # Correction loop
                for correction in range(self.config.num_corrections + 1):
                    self._process_timestep(
                        i_timestep=i,
                        current_time=current_time,
                        debug_output_file=debug_output_file,
                        update_states=False
                    )

        finally:
            # Close debug output file if it was opened
            if debug_output_file:
                debug_output_file.end()

            # End AeroDyn simulation
            try:
                self.adilib.adi_end()
            except Exception as e:
                print(f"Failed to end AeroDyn simulation: {e}")
                sys.exit(1)

        # Save results to output file
        out_file = adi.WriteOutChans(
            self.config.output_file, self.output_channel_names, self.output_channel_units
        )
        out_file.write(self.all_output_channel_values)
        out_file.end()
        print("Simulation completed successfully")

    def _initialize_simulation(self) -> None:
        """Sets up and initializes the AeroDyn simulation.

        Raises:
            SystemExit: If pre-initialization or initialization of AeroDyn fails
        """
        # Set initial positions and orientations
        self.adilib.initHubPos = self.init_hub_pos[0,:]
        self.adilib.initHubOrient = self.init_hub_orient[0,:]
        self.adilib.initNacellePos = self.init_nacelle_pos[0,:]
        self.adilib.initNacelleOrient = self.init_nacelle_orient[0,:]
        self.adilib.numBlades = self.config.num_blades
        self.adilib.initRootPos = self.init_root_pos
        self.adilib.initRootOrient = self.init_root_orient

        # Set mesh data
        self.adilib.numMeshPts = np.size(self.init_mesh_pos, 0)
        self.adilib.initMeshPos = self.init_mesh_pos
        self.adilib.initMeshOrient = self.init_mesh_orient
        self.adilib.meshPtToBladeNum = self.init_mesh_pt_to_blade_num

        #--------------------------------------
        # Initialize the library
        #--------------------------------------
        try:
            self.adilib.adi_preinit()
        except Exception as e:
            print(f"Failed to pre-initialize AeroDyn: {e}")
            sys.exit(1)

        # Setup rotor for each turbine
        self._setup_rotors()

        # Initialize with input files
        ad_input_lines = read_lines_from_file(self.config.primary_ad_file)
        ifw_input_lines = read_lines_from_file(self.config.primary_ifw_file)
        try:
            self.adilib.adi_init(ad_input_lines, ifw_input_lines)
        except Exception as e:
            print(f"Failed to initialize AeroDyn: {e}")
            sys.exit(1)

        # Store output channel information
        self.output_channel_names = self.adilib.output_channel_names
        self.output_channel_units = self.adilib.output_channel_units

        # Initialize output arrays
        self.output_channel_values = np.zeros(self.adilib.numChannels)
        self.all_output_channel_values = np.zeros((
            self.config.time_steps_to_run + 1, self.adilib.numChannels + 1
        ))
        self.disk_avg_vel = np.zeros(3)  # [Vx Vy Vz]

    def _setup_rotors(self) -> None:
        """Sets up rotors for all turbines in the simulation.

        Args:
            adilib: Instance of AeroDyn library to configure.
        """
        turb_ref_pos = [0., 0., 0.]
        for i in range(self.config.num_turbines):
            try:
                self.adilib.adi_setuprotor(i + 1, self.config.is_hawt, turb_ref_pos)
            except Exception as e:
                print(f"Failed to setup rotor for turbine {i + 1}: {e}")
                sys.exit(1)

    def _process_timestep(
        self,
        i_timestep: int,
        current_time: float,
        debug_output_file: Optional[adi.DriverDbg],
        update_states: bool = False
    ) -> None:
        """Calculate outputs for a single time step.

        Args:
            i_timestep: Current time step index
            current_time: Current simulation time
            debug_output_file: Debug output file handler
            update_states: Whether to update states before calculating outputs
        """
        # Get motion data for current timestep from vtk
        hub_pos, hub_orient, hub_vel, hub_acc = self._set_motion_hub(i_timestep)
        nac_pos, nac_orient, nac_vel, nac_acc = self._set_motion_nacelle(i_timestep)
        root_pos, root_orient, root_vel, root_acc = self._set_motion_root(i_timestep)
        mesh_pos, mesh_orient, mesh_vel, mesh_acc, mesh_forces_moments = self._set_motion_blade_mesh(i_timestep)

        # Set rotor motion for each turbine
        for i_turbine in range(self.config.num_turbines):
            try:
                self.adilib.adi_setrotormotion(
                    i_turbine + 1,  # 1-based indexing for turbines
                    hub_pos, hub_orient, hub_vel, hub_acc,
                    nac_pos, nac_orient, nac_vel, nac_acc,
                    root_pos, root_orient, root_vel, root_acc,
                    mesh_pos, mesh_orient, mesh_vel, mesh_acc
                )
            except Exception as e:
                print(f"Failed to set rotor motion at T={current_time}: {e}")
                raise

        # If not first time step, update states
        if i_timestep > 0:
            # Update states if requested and not at the end of simulation
            if update_states and i_timestep < self.config.time_steps_to_run:
                previous_time = (i_timestep - 1) * self.adilib.dt
                try:
                    self.adilib.adi_updateStates(previous_time, current_time)
                except Exception as e:
                    print(f"Failed to update states at T={current_time}: {e}")
                    if debug_output_file:
                        debug_output_file.end()
                    sys.exit(1)

            # Set rotor motion for each turbine
            for i_turbine in range(self.config.num_turbines):
                try:
                    self.adilib.adi_setrotormotion(
                        i_turbine + 1,  # 1-based indexing for turbines
                        hub_pos, hub_orient, hub_vel, hub_acc,
                        nac_pos, nac_orient, nac_vel, nac_acc,
                        root_pos, root_orient, root_vel, root_acc,
                        mesh_pos, mesh_orient, mesh_vel, mesh_acc
                    )
                except Exception as e:
                    print(f"Failed to set rotor motion at T={current_time}: {e}")
                    raise

        # Calculate outputs
        try:
            self.adilib.adi_calcOutput(current_time, self.output_channel_values)
        except Exception as e:
            print(f"Failed to calculate outputs at T={current_time}: {e}")
            raise

        # Get rotor loads and disk average velocity for each turbine
        for i_turbine in range(self.config.num_turbines):
            try:
                self.adilib.adi_getrotorloads(i_turbine + 1, mesh_forces_moments)
                self.adilib.adi_getdiskavgvel(i_turbine + 1, self.disk_avg_vel)
            except Exception as e:
                print(f"Failed to get rotor data at T={current_time}: {e}")
                raise

        # Write debug output if enabled
        if debug_output_file:
            debug_output_file.write(
                current_time, mesh_pos, mesh_vel, mesh_acc, mesh_forces_moments, self.disk_avg_vel
            )

        # Store outputs
        self.all_output_channel_values[i_timestep, :] = np.append(current_time, self.output_channel_values)

    def _set_motion_hub(self, i_timestep: int) -> tuple:
        """Gets hub motion parameters for the current time step.

        Args:
            i_timestep: Current time step number

        Returns:
            tuple: (hub_position, hub_orientation, hub_velocity, hub_acceleration)
        """
        return read_vtk_motion(
            self.config.vtk_dir, self.config.hub_mesh_root, i_timestep, self.config.vtk_field_len
        )

    def _set_motion_nacelle(self, i_timestep: int) -> tuple:
        """Gets nacelle motion parameters for the current time step.

        Args:
            i_timestep: Current time step number

        Returns:
            tuple: (nacelle_position, nacelle_orientation, nacelle_velocity, nacelle_acceleration)
        """
        return read_vtk_motion(
            self.config.vtk_dir, self.config.nac_mesh_root, i_timestep, self.config.vtk_field_len
        )

    def _set_motion_root(self, i_timestep: int) -> tuple:
        """Gets blade root motion parameters for the current time step.

        Args:
            i_timestep: Current time step number

        Returns:
            tuple: (root_positions, root_orientations, root_velocities, root_accelerations)
        """
        root_positions = np.zeros((self.config.num_blades, 3), dtype="float32")
        root_orientations = np.zeros((self.config.num_blades, 9), dtype="float64")
        root_velocities = np.zeros((self.config.num_blades, 6), dtype="float32")
        root_accelerations = np.zeros((self.config.num_blades, 6), dtype="float32")

        for k in range(self.config.num_blades):
            positions, orientations, velocities, accelerations = read_vtk_motion(
                self.config.vtk_dir,
                self.config.bld_root_mesh_root + str(k+1),
                i_timestep,
                self.config.vtk_field_len
            )
            root_positions[k, :] = positions
            root_orientations[k, :] = orientations
            root_velocities[k, :] = velocities
            root_accelerations[k, :] = accelerations

        return root_positions, root_orientations, root_velocities, root_accelerations

    def _set_motion_blade_mesh(self, i_timestep: int) -> tuple:
        """Gets blade mesh motion parameters for the current time step.

        Args:
            i_timestep: Current time step number

        Returns:
            tuple: (mesh_positions, mesh_orientations, mesh_velocities, mesh_accelerations, mesh_forces_moments)
        """
        mesh_positions = np.empty((0, 3), dtype="float32")
        mesh_orientations = np.empty((0, 9), dtype="float64")
        mesh_velocities = np.empty((0, 6), dtype="float32")
        mesh_accelerations = np.empty((0, 6), dtype="float32")
        mesh_forces_moments = np.zeros((sum(self.num_blade_node), 6))  # [Fx, Fy, Fz, Mx, My, Mz]

        for k in range(self.config.num_blades):
            positions, orientations, velocities, accelerations = read_vtk_motion(
                self.config.vtk_dir,
                self.config.bld_mesh_root + str(k+1),
                i_timestep,
                self.config.vtk_field_len
            )
            mesh_positions = np.concatenate((mesh_positions, positions))
            mesh_orientations = np.concatenate((mesh_orientations, orientations))
            mesh_velocities = np.concatenate((mesh_velocities, velocities))
            mesh_accelerations = np.concatenate((mesh_accelerations, accelerations))

        return mesh_positions, mesh_orientations, mesh_velocities, mesh_accelerations, mesh_forces_moments

if __name__ == "__main__":
    driver = AeroDynDriver(AeroDynConfig(), LibraryConfig())
    driver.run_simulation()
