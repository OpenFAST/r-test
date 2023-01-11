# -*- coding: utf-8 -*-
"""
Created on Fri Oct  1 14:00:45 2021

@author: elozon
"""
from moorpy.Catenary import catenary
import moorpy as mp 
import numpy as np 
import os
import sys
sys.path.insert(0, os.path.sep.join(["..","..","..","..", "lib"]))
import argparse
import shutil
import glob
import subprocess
import rtestlib as rtl
import pass_fail
import openfastDrivers
import pass_fail
from errorPlotting import exportCaseSummary
import MattLib as ml   # module in same folder
from moorpy.MoorProps import getLineProps

### This code is under development, intended to help with setting up and analyzing MoorDyn checks
### needs to be updated for most recent MoorPy version and made more user friendly 


def get_change(current, previous):
  if current == previous:
      return 0
  try:
      return (abs(current - previous) / previous) * 100.0
  except ZeroDivisionError:
      return float('inf')
  

def single_line_MP_MD_test(depth, anchorR, diameter, LineLength, typeName, executable, folder, tolerance, execute = True):
    '''Create a single line arrangement in MoorPy with fixed end points, run with MoorDyn driver, and compare tensions/positions

    Parameters
    ----------
    depth: water depth
    anchorR: spacing of anchor point from 0,0,0
    diameter: line diameter
    LineLength: length of line from anchor to 0,0,0
    typeName: string identifier of LineType object that this Line is to be
    executable: file path to moordyn driver exectuable - MUST include executable i.e. C:/code/openfast/executable/MoorDynDriver_x64.exe'
    folder: folder name for test case - must be subfolder of current working directory.  need to have driver input file in this folder already!
    tolerance: percent tolerance for pass/fail 
    execute: if True, runs moordyn driver 
        

    Returns
    -------
    None.

    '''
    cd = os.getcwd()
    testBuildDirectory = os.path.join(cd,folder)
    os.chdir(folder)
    
    #MoorPy system 
    test = mp.System()
    test.depth = depth
    
    # Create the LineType of the line for the system
    test.lineTypes[typeName] = getLineProps(diameter, name=typeName)
    
    # add two fixed points and one line
    test.addPoint(1, [   0, 0,    0])
    test.addPoint(1, [ anchorR, 0,  -test.depth])
    test.addLine(LineLength, typeName)
    
    # attach
    test.pointList[0].attachLine(1, 1)
    test.pointList[1].attachLine(1, 0)
    
    test.initialize(plots=1)
    test.solveEquilibrium3()
    test.plot()
    
    #MD input file
    md_call = ['CON2T','CON1T','CON1FX','CON1FY','CON1FZ','CON2FX','CON2FY','CON2FZ', 'L1N20PX','L1N20PY','L1N20PZ','L1N0PX','L1N0PY','L1N0PZ','L1N10PX','L1N10PY','L1N10PZ', 'L1N10T']
    test.unload_farm('test.dat', depth = test.depth, Outputs = md_call)
    
    #MD Driver input file
    test.unload_md_driver('md_driver.inp', depth = test.depth)
    
    
    ### Run MoorDyn on the test case
    if execute:
        caseInputFile = os.path.join(testBuildDirectory, "md_driver.inp")
        returnCode = openfastDrivers.runMoordynDriverCase(caseInputFile, executable)
        if returnCode != 0:
            rtl.exitWithError("")
       
    # Read in MD output
    data, units = ml.read_output_file("","driver.MD.out", skiplines=0)

    line = test.lineList[0]
    xs, ys, zs, t = line. getLineCoords(Time = 0)
    mp_vals = [line.TA, line.TB, line.fB[0],line.fB[1],line.fB[2] ,line.fA[0],line.fA[1],line.fA[2], line.rB[0], line.rB[1], line.rB[2], line.rA[0], line.rA[1], line.rA[2], xs[10], ys[10], zs[10], t[10]]
    print('--------- MoorDyn MoorPy Comparison Results -------')
    for i in range(0, len(md_call)):
        md_vals = data[md_call[i]]
        diff = get_change(np.mean(md_vals), mp_vals[i])
        #norm = pass_fail.calculate_relative_norm(md_vals.reshape(-1, 1), mp_vals[i].reshape(-1, 1))
        if abs(diff) < tolerance:
            print('Pass Check ', md_call[i])
        else:
            print('Fail Check ', md_call[i], ' by {:2.2f} %, MD = {:8.2f}, MP = {:8.2f}'.format(diff, np.mean(md_vals), mp_vals[i]))

def numSegs_MD_MD_test(depth, anchorR, diameter, LineLength, typeName, executable, folder, tolerance, nSegs = [20, 40], execute = True):
    '''Create a single line arrangement in MoorPy with fixed end points, run with MoorDyn driver, and compare tensions/positions

    Parameters
    ----------
    depth: water depth
    anchorR: spacing of anchor point from 0,0,0
    diameter: line diameter
    LineLength: length of line from anchor to 0,0,0
    typeName: string identifier of LineType object that this Line is to be
    executable: file path to moordyn driver exectuable - MUST include executable i.e. C:/code/openfast/executable/MoorDynDriver_x64.exe'
    folder: folder name for test case - must be subfolder of current working directory.  need to have driver input file in this folder already!
    tolerance: percent tolerance for pass/fail 
    execute: if True, runs moordyn driver 
        

    Returns
    -------
    None.

    '''
    cd = os.getcwd()
    testBuildDirectory = os.path.join(cd,folder)
    os.chdir(folder)
    
    
    filenames = ['test1.dat', 'test2.dat']
    drivernames = ['md_driver1.inp','md_driver2.inp']
    outroots = ['driver1','driver2']
    md_call = [[],[]]
    for i in range(0,2):
        #MoorPy system 
        test = mp.System()
        test.depth = depth
        
        # Create the LineType of the line for the system
        test.lineTypes[typeName] = getLineProps(diameter, name=typeName)
        
        # add two fixed points and one line
        test.addPoint(1, [   0, 0,    0])
        test.addPoint(1, [ anchorR, 0,  -test.depth])
        test.addLine(LineLength, typeName, nSegs = nSegs[i])
        
        # attach
        test.pointList[0].attachLine(1, 1)
        test.pointList[1].attachLine(1, 0)
        
        test.initialize(plots=1)
        test.solveEquilibrium3()
        test.plot()
        
        #MD input file
        md_call[i] = ['CON1FX','CON1FY','CON1FZ','CON2FX','CON2FY','CON2FZ', 'L1N'+str(nSegs[i])+'PX','L1N'+str(nSegs[i])+'PY','L1N'+str(nSegs[i])+'PZ','L1N0PX','L1N0PY','L1N0PZ','L1N'+str(int(nSegs[i]/2))+'PX',
                      'L1N'+str(int(nSegs[i]/2))+'PY','L1N'+str(int(nSegs[i]/2))+'PZ','L1N'+str(int(nSegs[i]/2))+'T']
        test.unload_farm(filenames[i], depth = test.depth, Outputs = md_call[i])
        
        #MD Driver input file
        test.unload_md_driver(drivernames[i], outroot = outroots[i] , MDinputfile = filenames[i],depth = test.depth)
        
        
        ### Run MoorDyn on the test case
        if execute:
            caseInputFile = os.path.join(testBuildDirectory, drivernames[i])
            returnCode = openfastDrivers.runMoordynDriverCase(caseInputFile, executable)
            if returnCode != 0:
                rtl.exitWithError("")
       
    # Read in MD output
    data1, units = ml.read_output_file("","driver1.MD.out", skiplines=0)
    data2, units = ml.read_output_file("","driver2.MD.out", skiplines=0)
    print('--------- MoorDyn MoorDyn Comparison Results -------')
    print('MD1 num segs = ', str(nSegs[0]), ', MD2 num segs = ', str(nSegs[1]))
    for i in range(0, len(md_call[0])):
        md_vals1 = data1[md_call[0][i]]
        md_vals2 = data2[md_call[1][i]]
        diff = get_change(np.mean(md_vals1), np.mean(md_vals2))
        norm = pass_fail.calculate_relative_norm(md_vals1.reshape(-1, 1), md_vals2.reshape(-1, 1))
        if abs(diff) < tolerance:
            print('Pass Check ', md_call[0][i])
        else:
            print('Fail Check ', md_call[0][i], ' by {:2.2f} %, MD1 = {:8.2f}, MD2 = {:8.2f}'.format(diff, np.mean(md_vals1), np.mean(md_vals2)))

def bridle_line_MP_MD_test(depth, anchorR, diameter, LineLength, typeName, executable, folder, tolerance, execute = True):
    '''IN PROGRESS Create a single line arrangement in MoorPy with fixed end points, run with MoorDyn driver, and compare tensions/positions
    
    Parameters
    ----------
    depth: water depth
    anchorR: spacing of anchor point from 0,0,0
    diameter: line diameter
    LineLength: length of line from anchor to 0,0,0
    typeName: string identifier of LineType object that this Line is to be
    executable: file path to moordyn driver exectuable - MUST include executable i.e. C:/code/openfast/executable/MoorDynDriver_x64.exe'
    folder: folder name for test case - must be subfolder of current working directory.  need to have driver input file in this folder already!
    tolerance: percent tolerance for pass/fail 
    execute: if True, runs moordyn driver 
        

    Returns
    -------
    None.

    '''
    cd = os.getcwd()
    testBuildDirectory = os.path.join(cd,folder)
    os.chdir(folder)
    
    #MoorPy system 
    test = mp.System()
    test.depth = depth
    
    # Create the LineType of the line for the system
    test.lineTypes[typeName] = getLineProps(diameter, name=typeName)
    
    # add two fixed points and one line
    test.addPoint(1, [   0, 0,    0])
    test.addPoint(1, [ anchorR, 0,  -test.depth])
    test.addLine(LineLength, typeName)
    
    # attach
    test.pointList[0].attachLine(1, 1)
    test.pointList[1].attachLine(1, 0)
    
    test.initialize(plots=1)
    test.solveEquilibrium3()
    test.plot()
    
    #MD input file
    md_call = ['CON2T','CON1T','CON1FX','CON1FY','CON1FZ','CON2FX','CON2FY','CON2FZ', 'L1N20PX','L1N20PY','L1N20PZ','L1N0PX','L1N0PY','L1N0PZ','L1N10PX','L1N10PY','L1N10PZ', 'L1N10T']
    test.unload_farm('test.dat', depth = test.depth, Outputs = md_call)
    
    #MD Driver input file
    test.unload_md_driver('md_driver.inp', depth = test.depth)
    
    
    ### Run MoorDyn on the test case
    if execute:
        caseInputFile = os.path.join(testBuildDirectory, "md_driver.inp")
        returnCode = openfastDrivers.runMoordynDriverCase(caseInputFile, executable)
        if returnCode != 0:
            rtl.exitWithError("")
       
    # Read in MD output
    data, units = ml.read_output_file("","driver.MD.out", skiplines=0)

    line = test.lineList[0]
    xs, ys, zs, t = line. getLineCoords(Time = 0)
    mp_vals = [line.TA, line.TB, line.fB[0],line.fB[1],line.fB[2] ,line.fA[0],line.fA[1],line.fA[2], line.rB[0], line.rB[1], line.rB[2], line.rA[0], line.rA[1], line.rA[2], xs[10], ys[10], zs[10], t[10]]
    print('--------- MoorDyn MoorPy Comparison Results -------')
    for i in range(0, len(md_call)):
        md_vals = data[md_call[i]]
        diff = get_change(np.mean(md_vals), mp_vals[i])
        #norm = pass_fail.calculate_relative_norm(md_vals.reshape(-1, 1), mp_vals[i].reshape(-1, 1))
        if abs(diff) < tolerance:
            print('Pass Check ', md_call[i])
        else:
            print('Fail Check ', md_call[i], ' by {:2.2f} %, MD = {:8.2f}, MP = {:8.2f}'.format(diff, np.mean(md_vals), mp_vals[i]))
                        

def numLines_MD_MD_test(depth, anchorR, diameter, LineLength, typeName, executable, folder, tolerance,  execute = True):
    '''Create a single line arrangement in MoorPy with fixed end points, run with MoorDyn driver, and compare tensions/positions

    Parameters
    ----------
    depth: water depth
    anchorR: spacing of anchor point from 0,0,0
    diameter: line diameter
    LineLength: length of line from anchor to 0,0,0
    typeName: string identifier of LineType object that this Line is to be
    executable: file path to moordyn driver exectuable - MUST include executable i.e. C:/code/openfast/executable/MoorDynDriver_x64.exe'
    folder: folder name for test case - must be subfolder of current working directory.  need to have driver input file in this folder already!
    tolerance: percent tolerance for pass/fail 
    execute: if True, runs moordyn driver 
        

    Returns
    -------
    None.

    '''
    cd = os.getcwd()
    testBuildDirectory = os.path.join(cd,folder)
    os.chdir(folder)
    
    
    filenames = ['test1.dat', 'test2.dat']
    drivernames = ['md_driver1.inp','md_driver2.inp']
    outroots = ['driver1','driver2']
    md_call = [[],[]]
    for i in range(0,2):
        #MoorPy system 
        test = mp.System()
        test.depth = depth
        
        # Create the LineType of the line for the system
        test.lineTypes[typeName] = getLineProps(diameter, name=typeName)
        
        # add two fixed points and one line
        if i == 0:
            test.addPoint(1, [   0, 0,    0])
            test.addPoint(1, [ anchorR, 0,  -test.depth])
            test.addLine(LineLength, typeName)
            # attach
            test.pointList[0].attachLine(1, 1)
            test.pointList[1].attachLine(1, 0)
        
        else:
            test.addPoint(1, [   0, 0,    0])
            test.addPoint(0, [ anchorR/2, 0,  -test.depth/2])
            test.addPoint(1, [ anchorR, 0,  -test.depth])
            test.addLine(LineLength/2, typeName)
            test.addLine(LineLength/2, typeName)
            test.pointList[0].attachLine(1,1)
            test.pointList[1].attachLine(1,0)
            test.pointList[1].attachLine(2,1)
            test.pointList[2].attachLine(2,0)
    
        test.initialize(plots=1)
        test.solveEquilibrium3()
        test.plot()
        
        #MD input file
        if i == 0:
            md_call[i] = ['CON1FX','CON1FY','CON1FZ','CON2FX','CON2FY','CON2FZ', 'L1N20PX','L1N20PY','L1N20PZ','L1N9PX','L1N10PY','L1N10PZ','L1N10T',
                      'L1N1PX','L1N1PY','L1N1PZ','L1N1T']
        else:
             md_call[i] = ['CON1FX','CON1FY','CON1FZ','CON3FX','CON3FY','CON3FZ', 'L1N20PX','L1N20PY','L1N20PZ','L1N0PX','L1N0PY','L1N0PZ','L1N0T',
                      'L2N2PX','L2N2PY','L2N2PZ','L2N2T']
        test.unload(filenames[i], depth = test.depth, Outputs = md_call[i])
        
        #MD Driver input file
        test.unload_md_driver(drivernames[i], outroot = outroots[i] , MDinputfile = filenames[i],depth = test.depth)
        
        
        ### Run MoorDyn on the test case
        if execute:
            caseInputFile = os.path.join(testBuildDirectory, drivernames[i])
            returnCode = openfastDrivers.runMoordynDriverCase(caseInputFile, executable)
            if returnCode != 0:
                rtl.exitWithError("")
       
    # Read in MD output
    data1, units = ml.read_output_file("","driver1.MD.out", skiplines=0)
    data2, units = ml.read_output_file("","driver2.MD.out", skiplines=0)
    print('--------- MoorDyn MoorDyn Comparison Results -------')
    print('MD1 num lines = 1, MD2 num lines = 2')
    for i in range(0, len(md_call[0])):
        md_vals1 = data1[md_call[0][i]]
        md_vals2 = data2[md_call[1][i]]
        diff = get_change(np.mean(md_vals1), np.mean(md_vals2))
        norm = pass_fail.calculate_relative_norm(md_vals1.reshape(-1, 1), md_vals2.reshape(-1, 1))
        if abs(diff) < tolerance:
            print('Pass Check ', md_call[0][i])
        else:
            print('Fail Check ', md_call[0][i], ' by {:2.2f} %, MD1 = {:8.2f}, MD2 = {:8.2f}'.format(diff, np.mean(md_vals1), np.mean(md_vals2)))

if __name__ ==  '__main__':
    tolerance = 0.1 #percent tolerance
    
    folder = 'test1'
    folder2 = 'test2'
    executable = 'C:/code/openfast/executable/MoorDynDriver_x64.exe'
    
    diameter = 120
    depth     = 600
    anchorR   = 1600                    # anchor radius/spacing
    LineLength= 1820
    typeName  = "chain"                 # identifier string for line type
    
    #single_line_MP_MD_test(depth, anchorR, diameter, LineLength, typeName, executable, folder, tolerance, execute = True)
    numLines_MD_MD_test(depth, anchorR, diameter, LineLength, typeName, executable, folder2, tolerance, execute = True)
