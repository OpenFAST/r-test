# Visualization Using ParaView


## ParaView State Files for Time-Domain Simulations
ParaView can save state files, which can then be loaded later. This is an easy way to apply the same template (glyphs, colors, scaling, etc.) to similar datasets. 

### Creating ParaView state files
When you have created a particular view in ParaView that you would like to save as a template for other OpenFAST simulations, click `File -> Save State ...` and choose a location and name for the file.

### Using ParaView state files
To use a state file:
1. Run OpenFAST with the appropriate modules and VTK inputs (`WrVTK`, `VTK_type`, `VTK_fields`) set for the template ParaView state file you want to use. For the easiest use of ParaView state files, 
   the name of the OpenFAST input file should have the same base name as the file used in the template.

2. Open ParaView, click `File -> Load State ...` and then select the appropriate `.pvsm` file. 
   - ParaView stores state files with absolute paths, so you will need to tell it the directory where the state data files are located. Choose `Search files under specified directory` in the `Load State Options` window, 
     and then specify the directory where OpenFAST wrote the `.vtp` files. Typically this is the `<OutPath>/vtk/` directory.

3. Tips
   - Make sure you have a version of ParaView newer than May 2017 so that the `Load State Options` window is available. Otherwise you will have to manually set the path for each file ParaView reads.
   - Note that state files load *on top of* whatever is open in ParaView, so if you load the state file twice, you will get two copies of all the files.
   - If your simulation generates files at more output times than were used in the state file, you can reload the files using `File -> Reload`. There should be an option that says 
     `This reader supports file series. Do you want to look for new files in the series and load those, or reload the existing files?` Choose `Find new files.`
   - Most of the VTK data OpenFAST outputs are "Unstructured Grid" datasets. 


## Visualization of Mode Shapes
*Note: These steps are followed in the Matlab script [AnalyzeModeShapes.m](AnalyzeModeShapes.m) contained in this directory.*

To visualize mode shapes:
1. Run OpenFAST for linearization analysis (`Linearize = true`) with `WrVTK = 3`. Note that if you would like to visualize the orientations, you should also set
   `VTK_fields = true` and `VTK_fps` to a value large enough to capture the motion of the mode shapes with the highest natural frequencies.
```
   OpenFAST.exe 5MW_Land_ModeShapes.fst
```
2. Run MBC3 analysis in Matlab. This will write a file named `ModesVizName` (a string set by the user). Note that this requires the [matlab-toolbox repository](https://github.com/OpenFAST/matlab-toolbox):
```
    MBC_data = fx_mbc3( LinFileNames, ModesVizName ); 
```
3. Run OpenFAST with the [visualization input file](ElastoDyn-Modes.viz):
```
   OpenFAST.exe -VTKLin ElastoDyn-Modes.viz
```
4. Run ParaView to view the mode shapes. You can either open the state file [ED_Surfaces.pvsm](ED_Surfaces.pvsm) inside ParaView, or
   you can use the included [Python script](plotModeShapes.py) to generate `avi` files of the mode shapes. See [Creating animations of the mode shapes](#creating-animations-of-the-mode-shapes)

### Creating animations of the mode shapes
To create animations of the mode shapes
- Manually
   1. Open the mode-shape state file, [ED_Surfaces.pvsm](ED_Surfaces.pvsm), using the instructions from the [time-domain section](#using-these-paraview-state-files) of this document.
   2. If necessary, select each mesh and reload the files (`File -> Reload Files` or `F5`), selecting the option to search for new files.
   3. Select `File -> Save Animation`. 
      - Type in a name for the animation file, and select the type of file to generate. Press `OK`.
      - In the "Save Animation Options" window that pops up, select `Save all views`, and set the `Frame Rate` that was used when you generated the vtk files in OpenFAST
       (check the summary file for the exact value used). Press `OK`.
- Using Python with ParaView
   1. Add ParaView's `bin` directory to your path. For example, on my Windows machine, I type:
```
   set path=C:\Program Files\ParaView 5.7.0-Windows-Python3.7-msvc2015-64bit\bin;%path%
```
      You will need to modify this if you have a different version of ParaView or have installed it in a different directory.
   2. Open [plotModeShapes.py](plotModeShapes.py), and edit variables at the top:
       - `mainDirName` is the name of the directory where the mode-shape vtk (.vtp) files are stored
       - `fileRootFmt` contains a format specifier for the root name of the `.vtp` files, excluding the mesh name. 
          Use `{:d}` in place of the mode number.
       - `nModes` is the number of modes to visualize (starts sequentially from mode 1)
       - `fps` is the number of frames per second that the vtk files were generated with (see the FAST summary file for the exact value)
         *Note: The current version of ParaView seems to ignore the frame rate that is specified when saving the animation.*
       - `StructureModule` is a string indicating the abbreviation of the structural model being used. This should be `"ED"` when ElastoDyn is used, or `"BD"` when BeamDyn is used.
   3. Run ParaView Python:
```
   pvpython plotModeShapes.py
```      

## Helpful links
- [Download ParaView](https://www.paraview.org/download/)
- [ParaView Online Wiki](https://www.paraview.org/Wiki/ParaView) Note that this also contains a tutorial on ParaView.
- [ParaView Python documentation]https://kitware.github.io/paraview-docs/latest/python/

