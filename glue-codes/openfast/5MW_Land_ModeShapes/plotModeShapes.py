from paraview.simple import * 
import os 


mainDirName =  os.getcwd() + '\\vtk\\'
fileRootFmt = '5MW_Land_ModeShapes.Mode{:d}.LinTime1.' # keep the format specifier {:d} for the mode number

nModes = 15  # number of modes to visualize
fps = 30 # frames per second (rate to save in the .avi file)

StructureModule = 'ED'
BladeMesh = "AD_Blade"

print('')
for iMode in range(nModes):  # iMode starts at 0, so add 1
   #fileRootName = fileRoot + str(iMode+1) + '.LinTime1.' #.LinTime1 depends on visualization options
   fileRootName = fileRootFmt.format(iMode+1)
   print('***' + fileRootName + '***')
   
   
   # determine number of leading zeros in this mode shape
   nLeadingZeros = 0
   exists = False
   while (not exists) and nLeadingZeros < 6:
      nLeadingZeros = nLeadingZeros + 1
      txt = '{:0' + str(nLeadingZeros) + 'd}'
      fileLeadingZeros = txt.format(1)
      Blade1File = mainDirName + fileRootName + BladeMesh + '1.' + fileLeadingZeros + '.vtp'
      exists = os.path.isfile(Blade1File)

   if not exists:
      print('  Could not find files to load.')
   else:
      LoadState('ED_Surfaces.pvsm', LoadStateDataFileOptions='Choose File Names',
          DataDirectory=mainDirName,
          a5MW_Land_DLL_WTurbMode1LinTime1AD_Blade10FileName=[Blade1File],
          a5MW_Land_DLL_WTurbMode1LinTime1AD_Blade20FileName=[mainDirName + fileRootName + BladeMesh + '2.' + fileLeadingZeros + '.vtp'],
          a5MW_Land_DLL_WTurbMode1LinTime1AD_Blade30FileName=[mainDirName + fileRootName + BladeMesh + '3.' + fileLeadingZeros + '.vtp'],
          a5MW_Land_DLL_WTurbMode1LinTime1Blade1Surface0FileName=[mainDirName + fileRootName + 'Blade1Surface.' + fileLeadingZeros + '.vtp'],
          a5MW_Land_DLL_WTurbMode1LinTime1Blade2Surface0FileName=[mainDirName + fileRootName + 'Blade2Surface.' + fileLeadingZeros + '.vtp'],
          a5MW_Land_DLL_WTurbMode1LinTime1Blade3Surface0FileName=[mainDirName + fileRootName + 'Blade3Surface.' + fileLeadingZeros + '.vtp'],
          a5MW_Land_DLL_WTurbMode1LinTime1ED_Hub0FileName=[mainDirName + fileRootName + StructureModule + '_Hub.' + fileLeadingZeros + '.vtp'],
          a5MW_Land_DLL_WTurbMode1LinTime1ED_Nacelle0FileName=[mainDirName + fileRootName + StructureModule + '_Nacelle.' + fileLeadingZeros + '.vtp'],
          a5MW_Land_DLL_WTurbMode1LinTime1ED_TowerLn2Mesh_motion0FileName=[mainDirName + fileRootName + StructureModule + '_TowerLn2Mesh_motion.' + fileLeadingZeros + '.vtp'],
          a5MW_Land_DLL_WTurbMode1LinTime1HubSurface0FileName=[mainDirName + fileRootName + 'HubSurface.' + fileLeadingZeros + '.vtp'],
          a5MW_Land_DLL_WTurbMode1LinTime1NacelleSurface0FileName=[mainDirName + fileRootName + 'NacelleSurface.' + fileLeadingZeros + '.vtp'],
          a5MW_Land_DLL_WTurbMode1LinTime1TowerSurface0FileName=[mainDirName + fileRootName  + 'TowerSurface.' + fileLeadingZeros + '.vtp']
      )



      ## find new sources
      # blade 1
      for iBlade in range(3):
         Blade = FindSource(fileRootName + BladeMesh + str(iBlade+1) + '...vtp')
         SetActiveSource(Blade)
         ExtendFileSeries(Blade)
         
         Blade = FindSource(fileRootName + 'Blade' + str(iBlade+1) + 'Surface...vtp')
         SetActiveSource(Blade)
         ExtendFileSeries(Blade)
         
      
      
      # hub
      Hub = FindSource(fileRootName + StructureModule + '_Hub...vtp')
      SetActiveSource(Hub)
      ExtendFileSeries(Hub)

      Hub = FindSource(fileRootName + 'HubSurface...vtp')
      SetActiveSource(Hub)
      ExtendFileSeries(Hub)

      
      # nacelle
      Nacelle = FindSource(fileRootName + StructureModule + '_Nacelle...vtp')
      SetActiveSource(Nacelle)
      ExtendFileSeries(Nacelle)

      Nacelle = FindSource(fileRootName + 'NacelleSurface...vtp')
      SetActiveSource(Nacelle)
      ExtendFileSeries(Nacelle)

      
      # tower
      Tower = FindSource(fileRootName + StructureModule + '_TowerLn2Mesh_motion...vtp')
      SetActiveSource(Tower)
      ExtendFileSeries(Tower)
      
      Tower = FindSource(fileRootName + 'TowerSurface...vtp')
      SetActiveSource(Tower)
      ExtendFileSeries(Tower)

      
      #####
      SetActiveView(GetRenderView()) 
      #view = GetActiveView() 
      layout = GetLayout()
      
      SaveAnimation(fileRootName + 'avi', viewOrLayout=layout, FrameRate=fps ) 
#      SaveAnimation(fileRootName + 'avi', viewOrLayout=layout, FrameRate=fps, ImageResolution=(1544,784) ) 
      # this .pvsm file defaults to (2734,1178) without ImageResolution arguments, resulting in a bunch of warnings
      # For some reason, ParaView is ignoring the FrameRate argument and always uses a value of 1.

      print('  Saved animation file.')


