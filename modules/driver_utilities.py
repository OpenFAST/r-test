import os
import sys
from pathlib import Path
from visread import *

def read_lines_from_file(file_path: str) -> list[str]:
    """Reads a file line by line, stripping whitespace.

    Args:
        file_path: Path to the file to read

    Returns:
        List of stripped lines from the file
    """
    return [line.rstrip() for line in open(file_path, "r")]

def read_vtk_motion(vtk_dir: str, base_name: str, time_step: int, field_len: int) -> tuple:
    """Reads position, orientation, velocity, and acceleration from a VTK file.

    Args:
        vtk_dir: Directory containing VTK files
        base_name: Base name of the VTK file
        time_step: Current time step number
        field_len: Length of the time field in filename

    Returns:
        tuple: (positions, orientations, velocities, accelerations)
    """
    time_field = str(time_step).zfill(field_len)
    file_path = os.path.sep.join([vtk_dir, f"{base_name}.{time_field}.vtp"])
    positions, orientations, num_pts = read_current_positions_from_vtk(file_path)
    velocities, accelerations = read_velocities_and_accelerations_from_vtk(file_path, num_pts)
    return positions, orientations, velocities, accelerations

def get_library_path() -> str:
    """Determines the correct library path based on platform.

    Returns:
        str: Path to the AeroDyn library for the current platform.

    Raises:
        ValueError: If the current platform is not supported.
        SystemExit: If on Windows and the DLL cannot be found in expected locations.
    """
    basename = "libaerodyn_inflow_c_binding"
    build_path = Path("..").joinpath(*[".."] * 4, "build")

    if sys.platform in ["linux", "linux2"]:
        return str(build_path / "modules" / "aerodyn" / f"{basename}.so")

    if sys.platform == "darwin":
        return str(build_path / "modules" / "aerodyn" / f"{basename}.dylib")

    if sys.platform == "win32":
        bit_version = "Win32" if sys.maxsize <= 2**32 else "x64"
        possible_paths = [
            build_path / "modules" / "aerodyn" / f"{basename}.dll",
            build_path / "bin" / f"AeroDyn_Inflow_c_binding_{bit_version}.dll"
        ]
        return str(next((path for path in possible_paths if path.is_file()), None)) or sys.exit(
            f"Python is {bit_version} bit and cannot find {bit_version} "
            f"bit InflowWind DLL in any expected location."
        )

    raise ValueError(f"Unsupported platform: {sys.platform}")
