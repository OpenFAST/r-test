import numpy as np
import vtk

def visread_positions(filename):
    reader = vtk.vtkXMLPolyDataReader()

    reader.SetFileName(filename)
    reader.Update()

    position_ar = np.array( reader.GetOutput().GetPoints().GetData(),  dtype="float32")
    _orientX = np.array( reader.GetOutput().GetPointData().GetArray(0),dtype="float64")
    _orientY = np.array( reader.GetOutput().GetPointData().GetArray(1),dtype="float64")
    _orientZ = np.array( reader.GetOutput().GetPointData().GetArray(2),dtype="float64")

    orient_ar = np.hstack((_orientX, _orientY, _orientZ))

    numpts_pos = np.size(position_ar,0)
    numpts_ori = np.size(orient_ar,0)

    if numpts_pos != numpts_ori:
        raise Exception("\nvisread_positions: Number of position and orientation points differ in file "+filename)

    return position_ar, orient_ar, numpts_pos
