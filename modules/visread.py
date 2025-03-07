import numpy as np
import vtk
from typing import Tuple, List

def _setup_vtk_reader(filename: str) -> Tuple[vtk.vtkXMLPolyDataReader, List[str]]:
    """Set up VTK reader and return reader object with array names.

    Args:
        filename: Path to VTK file
    Returns:
        Tuple of (reader object, list of array names)
    """
    reader = vtk.vtkXMLPolyDataReader()
    reader.SetFileName(filename)
    reader.Update()

    array_names = [
        reader.GetPointArrayName(i) for i in range(reader.GetNumberOfPointArrays())
    ]
    return reader, array_names

def _read_positions(filename: str, orientation_prefix: str = '') -> Tuple[np.ndarray, np.ndarray, int]:
    """Common implementation for reading positions and orientations.

    Args:
        filename: Path to VTK file
        orientation_prefix: Prefix for orientation array names ('' or 'Ref')
    """
    reader, array_names = _setup_vtk_reader(filename)

    # Read position array
    position_array = np.array(reader.GetOutput().GetPoints().GetData(), dtype="float32")

    # Read orientation arrays
    orient_components = []
    for axis in ['X', 'Y', 'Z']:
        array_name = f'{orientation_prefix}Orientation{axis}'
        orient_data = np.array(
            reader.GetOutput().GetPointData().GetArray(array_names.index(array_name)),
            dtype="float64"
        )
        orient_components.append(orient_data)

    orient_array = np.hstack(orient_components)

    num_pts_position = position_array.shape[0]
    num_pts_orientation = orient_array.shape[0]

    if num_pts_position != num_pts_orientation:
        raise Exception(f"\nread_positions: Number of position and orientation points differ in file {filename}")

    return position_array, orient_array, num_pts_position

def read_reference_positions_from_vtk(filename: str) -> Tuple[np.ndarray, np.ndarray, int]:
    """Read reference positions and orientations from VTK file."""
    return _read_positions(filename, orientation_prefix='Ref')

def read_current_positions_from_vtk(filename: str) -> Tuple[np.ndarray, np.ndarray, int]:
    """Read positions and orientations from VTK file."""
    return _read_positions(filename, orientation_prefix='')

def read_velocities_and_accelerations_from_vtk(filename: str, num_pts: int) -> Tuple[np.ndarray, np.ndarray]:
    """Read velocities and accelerations from VTK file.

    Args:
        filename: Path to VTK file
        num_pts: Expected number of points
    Returns:
        Tuple of (velocities array, accelerations array)
    """
    reader, array_names = _setup_vtk_reader(filename)

    # Helper function to read array or return zeros if not present
    def get_array_or_zeros(name: str) -> np.ndarray:
        if name in array_names:
            data = np.array(
                reader.GetOutput().GetPointData().GetArray(array_names.index(name)),
                dtype="float32"
            )
            if data.shape[0] != num_pts:
                raise Exception(
                    f"\nvisread_velacc: Unexpected number of {name} points in file {filename}"
                    f" (expected {num_pts}, got {data.shape[0]})"
                )
            return data
        return np.zeros((num_pts, 3), dtype="float32")

    # Read velocities
    translational_velocity = get_array_or_zeros('TranslationalVelocity')
    rotational_velocity = get_array_or_zeros('RotationalVelocity')
    velocities_array = np.hstack((translational_velocity, rotational_velocity))

    # Read accelerations
    translational_acceleration = get_array_or_zeros('TranslationalAcceleration')
    rotational_acceleration = get_array_or_zeros('RotationalAcceleration')
    accelerations_array = np.hstack((translational_acceleration, rotational_acceleration))

    return velocities_array, accelerations_array
