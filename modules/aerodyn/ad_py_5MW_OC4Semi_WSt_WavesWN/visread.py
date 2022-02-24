import numpy as np
import vtk

def visread_positions_ref(filename):
    reader = vtk.vtkXMLPolyDataReader()

    reader.SetFileName(filename)
    reader.Update()

    _arName = []
    _numArrays = reader.GetNumberOfPointArrays()
    for i in range(_numArrays):
        _arName.append(reader.GetPointArrayName(i))

    position_ar = np.array( reader.GetOutput().GetPoints().GetData(),  dtype="float32")
    _orientX = np.array( reader.GetOutput().GetPointData().GetArray(_arName.index('RefOrientationX')),dtype="float64")
    _orientY = np.array( reader.GetOutput().GetPointData().GetArray(_arName.index('RefOrientationY')),dtype="float64")
    _orientZ = np.array( reader.GetOutput().GetPointData().GetArray(_arName.index('RefOrientationZ')),dtype="float64")

    orient_ar = np.hstack((_orientX, _orientY, _orientZ))

    numpts_pos = np.size(position_ar,0)
    numpts_ori = np.size(orient_ar,0)

    if numpts_pos != numpts_ori:
        raise Exception("\nvisread_positions: Number of position and orientation points differ in file "+filename)

    return position_ar, orient_ar, numpts_pos


def visread_positions(filename):
    reader = vtk.vtkXMLPolyDataReader()

    reader.SetFileName(filename)
    reader.Update()

    _arName = []
    _numArrays = reader.GetNumberOfPointArrays()
    for i in range(_numArrays):
        _arName.append(reader.GetPointArrayName(i))

    position_ar = np.array( reader.GetOutput().GetPoints().GetData(),  dtype="float32")
    _orientX = np.array( reader.GetOutput().GetPointData().GetArray(_arName.index('OrientationX')),dtype="float64")
    _orientY = np.array( reader.GetOutput().GetPointData().GetArray(_arName.index('OrientationY')),dtype="float64")
    _orientZ = np.array( reader.GetOutput().GetPointData().GetArray(_arName.index('OrientationZ')),dtype="float64")

    orient_ar = np.hstack((_orientX, _orientY, _orientZ))

    numpts_pos = np.size(position_ar,0)
    numpts_ori = np.size(orient_ar,0)

    if numpts_pos != numpts_ori:
        raise Exception("\nvisread_positions: Number of position and orientation points differ in file "+filename)

    return position_ar, orient_ar, numpts_pos


def visread_velacc(filename,numpts):
    reader = vtk.vtkXMLPolyDataReader()

    reader.SetFileName(filename)
    reader.Update()

    _arName = []
    _numArrays = reader.GetNumberOfPointArrays()
    for i in range(_numArrays):
        _arName.append(reader.GetPointArrayName(i))

    if 'TranslationalVelocity' in _arName:
        _TV = np.array( reader.GetOutput().GetPointData().GetArray(_arName.index('TranslationalVelocity')),dtype="float32")
        if np.size(_TV,0) != numpts:
            raise Exception("\nvisread_velacc: Unexpected number of translational velocity points in file"+filename+" (expected "+str(numpts)+", got "+str(np.size(_TV,0))+")")
    else:
        _TV = np.zeros((numpts,3),dtype="float32")
    if 'RotationalVelocity' in _arName:
        _RV = np.array( reader.GetOutput().GetPointData().GetArray(_arName.index('RotationalVelocity'   )),dtype="float32")
        if np.size(_RV,0) != numpts:
            raise Exception("\nvisread_velacc: Unexpected number of rotational velocity points in file"+filename+" (expected "+str(numpts)+", got "+str(np.size(_RV,0))+")")
    else:
        _RV = np.zeros((numpts,3),dtype="float32")
    vel_ar = np.hstack((_TV, _RV))

    if 'TranslationalAcceleration' in _arName:
        _TA = np.array( reader.GetOutput().GetPointData().GetArray(_arName.index('TranslationalAcceleration')),dtype="float32")
        if np.size(_TA,0) != numpts:
            raise Exception("\nvisread_velacc: Unexpected number of translational acceleration points in file"+filename+" (expected "+str(numpts)+", got "+str(np.size(_TA,0))+")")
    else:
        _TA = np.zeros((numpts,3),dtype="float32")
    if 'RotationalAcceleration' in _arName:
        _RA = np.array( reader.GetOutput().GetPointData().GetArray(_arName.index('RotationalAcceleration'   )),dtype="float32")
        if np.size(_RA,0) != numpts:
            raise Exception("\nvisread_velacc: Unexpected number of rotational acceleration points in file"+filename+" (expected "+str(numpts)+", got "+str(np.size(_RA,0))+")")
    else:
        _RA = np.zeros((numpts,3),dtype="float32")
    acc_ar = np.hstack((_TA, _RA))

    return vel_ar, acc_ar
