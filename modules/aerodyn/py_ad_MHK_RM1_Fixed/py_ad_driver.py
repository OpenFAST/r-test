#-------------------------------------------------------------------------------
# LICENSING
#-------------------------------------------------------------------------------
# Copyright (C) 2026-present by National Laboratory of the Rockies (NLR)
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
# Overview
#-------------------------------------------------------------------------------
# Python driver for the AeroDyn x InflowWind C-bindings, specialized for the
# fixed MHK RM1 turbine.  In addition to the normal motion-replay workflow used
# by the other py_ad_* tests, this driver calls
# ADI_C_CalcOutput_and_AddedMass at every timestep and verifies that the blade
# added-mass matrices are nonzero (added mass is only nonzero for MHK turbines).
# The per-node 6x6 added-mass blocks for the final timestep are written to
# py_ad_driver_addedmass.out for direct inspection.

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
from pyOpenFAST import aerodyn_inflow

#--------------------------------------
# Library paths
#--------------------------------------
modules_path = Path(__file__).parent.joinpath(*[".."]*5, "reg_tests", "r-test", "modules")
print(f"Importing 'driver_utilities' from {modules_path}")
sys.path.insert(0, str(modules_path))
from driver_utilities import *

#-------------------------------------------------------------------------------
# Configuration classes
#-------------------------------------------------------------------------------
@dataclass
class AeroDynConfig:
    """Configuration settings for AeroDyn simulation."""
    # Simulation settings
    num_turbines: int = 1          # Number of turbines
    is_hawt: int = 1               # 1: HAWT (axial-flow MHK), 0: VAWT or cross-flow
    num_blades: int = 2            # Number of blades
    vtk_field_len: int = 3         # Length of the time field in filename
    time_steps_to_run: int = 20    # Number of time steps to run
    num_corrections: int = 0       # Number of corrections to perform
    debug_outputs: int = 0         # For checking the interface, set this to 1

    # Added-mass check: minimum acceptable peak |added mass| (kg or kg-m^2)
    added_mass_tol: float = 1.0e-6

    # Tolerances for comparing the computed added mass against the reference
    added_mass_rtol: float = 1.0e-5
    added_mass_atol: float = 1.0e-6

    #--------------------------------------
    # File names
    #--------------------------------------
    vtk_dir: str = "vtkRef"
    primary_ad_file: str = "ad_primary.dat"
    primary_ifw_file: str = "ifw_primary.dat"
    debug_output_file: str = "DbgOutputs.out"
    output_file: str = "py_ad_driver.out"
    added_mass_file: str = "py_ad_driver_addedmass.out"
    added_mass_ref_file: str = "py_ad_driver_addedmass.ref.txt"

    # Mesh root names
    hub_mesh_root: str = "AD_HubMotion"
    nac_mesh_root: str = "AD_Nacelle"
    bld_root_mesh_root: str = "AD_BladeRootMotion"
    bld_mesh_root: str = "AD_BladeMotion"

@dataclass
class LibraryConfig:
    """Configuration settings for AeroDyn library (MHK RM1 sea water properties)."""
    interpolation_order: int = 2                     # Order of the interpolation
    dt: float = 0.1                                  # Time interval for ADI calls
    gravity: float = 9.80665                         # Gravitational acceleration (m/s^2)
    fluid_density: float = 1025.0                    # Sea water density (kg/m^3)
    kinematic_viscosity: float = 1.06E-06            # Kinematic viscosity of sea water (m^2/s)
    sound_speed: float = 1500.0                      # Speed of sound in sea water (m/s)
    atmospheric_pressure: float = 101325.0           # Atmospheric pressure (Pa)
    vapor_pressure: float = 2500.0                   # Vapour pressure of sea water (Pa)
    water_depth: float = 50.0                        # Water depth (m)
    mean_sea_level_offset: float = 0.0               # Offset between still-water level and mean sea level (m)
    store_hub_height_velocity: bool = False          # Store horizontal hub velocity
    write_vtk: int = 0                               # animation (0: off, 1: init only, 2: all timesteps)
    vtk_type: int = 3                                # surface and line meshes
    transpose_dcm: int = 1                           # 0=false, 1=true

#-------------------------------------------------------------------------------
# Main driver class
#-------------------------------------------------------------------------------
class AeroDynDriver:
    """Main driver class for AeroDyn simulation with added-mass verification."""

    def __init__(self, config: AeroDynConfig, lib_config: LibraryConfig):
        """Initialize the AeroDyn driver with configuration settings."""
        self.config = config
        self.lib_config = lib_config

        # Initialize mesh data structures
        self._initialize_mesh_data()

        # Initialize library
        self.adilib = self._initialize_library()

        # Initialize output arrays as placeholders
        self.output_channel_values = None
        self.all_output_channel_values = None

        # Added-mass tracking
        self.node_added_mass = None
        self.peak_added_mass = 0.0
        self.last_added_mass = None

    def _initialize_mesh_data(self) -> None:
        """Initializes mesh data from VTK files for hub, nacelle, and blades."""
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

            tmp_pt_to_blade_num = np.full(num_pts, i+1, dtype=int)
            self.init_mesh_pt_to_blade_num = np.concatenate(
                (self.init_mesh_pt_to_blade_num, tmp_pt_to_blade_num)
            )

    def _initialize_library(self) -> aerodyn_inflow.AeroDynInflowLib:
        """Initialize the AeroDyn library with configuration settings."""
        library_path = get_library_path(module_name="aerodyn")

        try:
            adilib = aerodyn_inflow.AeroDynInflowLib(library_path)
        except Exception as e:
            print(f"Failed to load AeroDyn library at {library_path}: {e}")
            sys.exit(1)

        adilib.interpolation_order = self.lib_config.interpolation_order
        adilib.dt = self.lib_config.dt
        adilib.num_time_steps = self.config.time_steps_to_run
        adilib.gravity = self.lib_config.gravity
        adilib.fluid_density = self.lib_config.fluid_density
        adilib.kinematic_viscosity = self.lib_config.kinematic_viscosity
        adilib.sound_speed = self.lib_config.sound_speed
        adilib.atmospheric_pressure = self.lib_config.atmospheric_pressure
        adilib.vapor_pressure = self.lib_config.vapor_pressure
        adilib.water_depth = self.lib_config.water_depth
        adilib.mean_sea_level_offset = self.lib_config.mean_sea_level_offset
        adilib.num_turbines = self.config.num_turbines

        adilib.store_hub_height_velocity = self.lib_config.store_hub_height_velocity
        adilib.write_vtk = self.lib_config.write_vtk
        adilib.vtk_type = self.lib_config.vtk_type
        adilib.transpose_dcm = self.lib_config.transpose_dcm

        # MHK turbine flag (enables buoyancy and blade added mass)
        adilib.mhk = 1

        return adilib

    def run_simulation(self) -> None:
        """Run the main simulation with time stepping."""
        self._initialize_simulation()

        time = np.arange(0.0, (self.config.time_steps_to_run + 1) * self.adilib.dt, self.adilib.dt)

        debug_output_file = None
        if self.config.debug_outputs == 1:
            debug_output_file = aerodyn_inflow.DriverDbg(self.config.debug_output_file, self.adilib.num_mesh_pts)

        try:
            print(f"Time step: 0 at {time[0]}")
            self._process_timestep(0, time[0], 0.0, debug_output_file)

            for i in range(1, len(time)):
                print(f"Time step: {i} at {time[i]}")
                for correction in range(self.config.num_corrections + 1):
                    self._process_timestep(
                        i_step=i,
                        current_time=time[i],
                        prev_time=time[i-1],
                        debug_output_file=debug_output_file,
                        correction_step=correction
                    )

        finally:
            if debug_output_file:
                debug_output_file.end()
            try:
                self.adilib.adi_end()
            except Exception as e:
                print(f"Failed to end AeroDyn simulation: {e}")
                sys.exit(1)

        # Write output file with channel data
        out_file = aerodyn_inflow.WriteOutChans(
            self.config.output_file,
            self.adilib.output_channel_names,
            self.adilib.output_channel_units
        )
        out_file.write(self.all_output_channel_values)
        out_file.end()

        # Write the added-mass matrices for the final timestep, verify nonzero,
        # and compare against the stored reference.
        self._write_added_mass()
        self._verify_added_mass()
        self._compare_added_mass()

        print("Simulation completed successfully")

    def _initialize_simulation(self) -> None:
        """Initialize the AeroDyn simulation."""
        self.adilib.init_hub_pos = self.init_hub_pos[0, :]
        self.adilib.init_hub_orient = self.init_hub_orient[0, :]
        self.adilib.init_nacelle_pos = self.init_nacelle_pos[0, :]
        self.adilib.init_nacelle_orient = self.init_nacelle_orient[0, :]
        self.adilib.num_blades = self.config.num_blades
        self.adilib.init_root_pos = self.init_root_pos
        self.adilib.init_root_orient = self.init_root_orient

        self.adilib.num_mesh_pts = np.size(self.init_mesh_pos, 0)
        self.adilib.init_mesh_pos = self.init_mesh_pos
        self.adilib.init_mesh_orient = self.init_mesh_orient
        self.adilib.mesh_pt_to_blade_num = self.init_mesh_pt_to_blade_num

        try:
            self.adilib.adi_preinit()
        except Exception as e:
            print(f"Failed to pre-initialize AeroDyn: {e}")
            sys.exit(1)

        self._setup_rotors()

        ad_input_lines = read_lines_from_file(self.config.primary_ad_file)
        ifw_input_lines = read_lines_from_file(self.config.primary_ifw_file)

        try:
            self.adilib.adi_init(ad_input_lines, ifw_input_lines)
        except Exception as e:
            print(f"Failed to initialize AeroDyn: {e}")
            sys.exit(1)

        self.output_channel_values = np.zeros(self.adilib.num_channels)
        self.all_output_channel_values = np.zeros((
            self.config.time_steps_to_run + 1, self.adilib.num_channels + 1
        ))

        # Added-mass array: (num_turbines*num_mesh_pts, 6, 6)
        total_mesh_pts = self.config.num_turbines * self.adilib.num_mesh_pts
        self.node_added_mass = np.zeros((total_mesh_pts, 6, 6), dtype="float32")

    def _setup_rotors(self) -> None:
        """Setup rotors for all turbines in the simulation."""
        for i_turb in range(1, self.config.num_turbines + 1):
            turb_ref_pos = [0, 0, 0]
            try:
                self.adilib.adi_setuprotor(i_turb, self.config.is_hawt, turb_ref_pos)
            except Exception as e:
                print(f"Failed to setup rotor for turbine {i_turb}: {e}")
                sys.exit(1)

    def _process_timestep(
        self,
        i_step: int,
        current_time: float,
        prev_time: float,
        debug_output_file: Optional[aerodyn_inflow.DriverDbg] = None,
        correction_step: int = 0
    ) -> None:
        """Process a single timestep, computing outputs and added mass."""
        hub_pos, hub_orient, hub_vel, hub_acc = self._set_motion_hub(i_step)
        nac_pos, nac_orient, nac_vel, nac_acc = self._set_motion_nacelle(i_step)
        root_pos, root_orient, root_vel, root_acc = self._set_motion_root(i_step)
        mesh_pos, mesh_orient, mesh_vel, mesh_acc, mesh_forces_moments = self._set_motion_blade_mesh(i_step)

        hub_motion = aerodyn_inflow.MotionData(hub_pos, hub_orient, hub_vel, hub_acc)
        nac_motion = aerodyn_inflow.MotionData(nac_pos, nac_orient, nac_vel, nac_acc)
        root_motion = aerodyn_inflow.MotionData(root_pos, root_orient, root_vel, root_acc)
        mesh_motion = aerodyn_inflow.MotionData(mesh_pos, mesh_orient, mesh_vel, mesh_acc)

        i_turb = 1  # Hard-coded to one turbine for now
        try:
            self.adilib.adi_setrotormotion(
                i_turb, hub_motion, nac_motion, root_motion, mesh_motion
            )
        except Exception as e:
            print(f"Failed to set rotor motion at T={current_time}: {e}")
            raise

        if i_step > 0 and correction_step == 0:
            try:
                self.adilib.adi_updateStates(prev_time, current_time)
            except Exception as e:
                print(f"Failed to update states at T={current_time}: {e}")
                raise

        # Calculate outputs and the per-node added-mass matrices
        try:
            self.adilib.adi_calcOutput_and_addedMass(
                current_time, self.output_channel_values, self.node_added_mass
            )
        except Exception as e:
            print(f"Failed to calculate outputs/added mass at T={current_time}: {e}")
            raise

        # Track the peak added-mass magnitude and store the last timestep's matrices
        self.peak_added_mass = max(self.peak_added_mass, float(np.max(np.abs(self.node_added_mass))))
        self.last_added_mass = self.node_added_mass.copy()

        # Get rotor loads (remainder loads after removing the added-mass contribution)
        try:
            self.adilib.adi_getrotorloads(i_turb, mesh_forces_moments)
        except Exception as e:
            print(f"Failed to get rotor loads at T={current_time}: {e}")
            raise

        if debug_output_file:
            debug_output_file.write(current_time, mesh_pos, mesh_vel, mesh_acc, mesh_forces_moments)

        self.all_output_channel_values[i_step, :] = np.append(current_time, self.output_channel_values)

    def _write_added_mass(self) -> None:
        """Write the final-timestep per-node 6x6 added-mass blocks to a file."""
        if self.last_added_mass is None:
            return
        with open(self.config.added_mass_file, "w") as fh:
            fh.write("# Per-node blade added-mass matrices (final timestep), global frame.\n")
            fh.write("# One node per block; each block is the node's 6x6 matrix (rows Fx,Fy,Fz,Mx,My,Mz).\n")
            fh.write(f"# num_nodes = {self.last_added_mass.shape[0]}\n")
            fh.write(f"# peak_abs_added_mass = {self.peak_added_mass:.6e}\n")
            for node in range(self.last_added_mass.shape[0]):
                fh.write(f"node {node+1}\n")
                for row in range(6):
                    fh.write("  " + " ".join(f"{v: .6e}" for v in self.last_added_mass[node, row, :]) + "\n")

    def _verify_added_mass(self) -> None:
        """Verify the blade added mass is nonzero (it must be for an MHK turbine)."""
        if self.peak_added_mass <= self.config.added_mass_tol:
            raise RuntimeError(
                f"Blade added mass is effectively zero (peak |added mass| = "
                f"{self.peak_added_mass:.6e} <= tol {self.config.added_mass_tol:.6e}). "
                f"Expected nonzero added mass for the MHK RM1 turbine."
            )
        print(f"Added-mass check passed: peak |added mass| = {self.peak_added_mass:.6e}")

    def _read_added_mass_file(self, path: str) -> np.ndarray:
        """Read per-node 6x6 added-mass blocks written in the _write_added_mass format."""
        blocks = []
        rows = []
        with open(path) as fh:
            for line in fh:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                if s.startswith("node"):
                    if rows:
                        blocks.append(rows)
                        rows = []
                    continue
                rows.append([float(v) for v in s.split()])
        if rows:
            blocks.append(rows)
        return np.array(blocks, dtype="float64")

    def _compare_added_mass(self) -> None:
        """Compare the final-timestep added-mass matrices against the stored reference."""
        if self.last_added_mass is None:
            return
        ref_path = self.config.added_mass_ref_file
        if not os.path.isfile(ref_path):
            print(f"Added-mass reference '{ref_path}' not found; skipping comparison.")
            return
        ref = self._read_added_mass_file(ref_path)
        cur = np.asarray(self.last_added_mass, dtype="float64")
        if ref.shape != cur.shape:
            raise RuntimeError(
                f"Added-mass reference shape {ref.shape} does not match computed {cur.shape}."
            )
        max_abs_diff = float(np.max(np.abs(cur - ref)))
        if not np.allclose(cur, ref, rtol=self.config.added_mass_rtol, atol=self.config.added_mass_atol):
            raise RuntimeError(
                f"Added-mass matrices differ from reference (max abs diff = {max_abs_diff:.6e}, "
                f"rtol = {self.config.added_mass_rtol:.1e}, atol = {self.config.added_mass_atol:.1e})."
            )
        print(f"Added-mass reference comparison passed (max abs diff = {max_abs_diff:.6e}).")

    def _set_motion_hub(self, i_timestep: int) -> tuple:
        return read_vtk_motion(
            self.config.vtk_dir, self.config.hub_mesh_root, i_timestep, self.config.vtk_field_len
        )

    def _set_motion_nacelle(self, i_timestep: int) -> tuple:
        return read_vtk_motion(
            self.config.vtk_dir, self.config.nac_mesh_root, i_timestep, self.config.vtk_field_len
        )

    def _set_motion_root(self, i_timestep: int) -> tuple:
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
