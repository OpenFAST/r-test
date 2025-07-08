import os
import sys
from pathlib import Path
from visread import *

def get_library_path(module_name: str) -> str:
    """Determines the correct library path based on platform and module name.

    Args:
        module_name: Name of the module

    Returns:
        str: Path to the module library for the current platform.

    Raises:
        ValueError: If the current platform is not supported.
        SystemExit: If on Windows and the DLL cannot be found in expected locations.
    """
    # Map module names to their library base names
    module_map = {
        "aerodyn": "libaerodyn_inflow_c_binding",
        "hydrodyn": "libhydrodyn_c_binding",
        "inflowwind": "libifw_c_binding",
        "moordyn": "libmoordyn_c_binding"
    }
    basename = module_map.get(module_name.lower(), f"lib{module_name}_c_binding")
    build_path = Path("..").joinpath(*[".."] * 3)    # for running from testing in a build dir

    if sys.platform in ["linux", "linux2"]:
        ext = "so"
    if sys.platform == "darwin":
        ext = "dylib"

    if sys.platform in ["linux","linux2","darwin"]:
        possible_paths = [
            build_path / "modules" / module_name /  f"{basename}.{ext}",
            build_path / ".." / "install" / "lib" / f"{basename}.{ext}"
        ]
        for path in possible_paths:
            if path.is_file():
                print(f"Loading library from {path}")
                return str(path)
        sys.exit(
            f"Cannot find lib{module_name}_c_binding at"
            f"      {possible_paths[0]} or {possible_paths[1]}"
        )

    if sys.platform == "win32":
        bit_version = "Win32" if sys.maxsize <= 2**32 else "x64"
        possible_paths = [
            build_path / "modules" / module_name / f"{basename}.dll",
            build_path / "bin" / f"{module_name}_c_binding_{bit_version}.dll"
        ]
        for path in possible_paths:
            if path.is_file():
                print(f"Loading library from {path}")
                return str(path)
        sys.exit(
            f"Python is {bit_version} bit and cannot find {bit_version} "
            f"bit {module_name} DLL at {path}."
        )

    raise ValueError(f"Unsupported platform: {sys.platform}")

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
