openFASTexe = '..\..\..\..\..\build\bin\openFAST_Win32.exe';

RootName = '5MW_Land_ModeShapes.';

%% run OpenFAST (saves checkpoint file)
system([ openFASTexe ' ' RootName 'fst']);
%%
% run mbc3 (saves eigenvectors)
LinFileNames = strcat( RootName, strrep( cellstr(num2str( (1:36)' )), ' ', ''), '.lin' );
[MBC]=fx_mbc3( LinFileNames, 'EigenvectorsForModeShapeVTK.bin' );

%%
% restart OpenFAST to generate vtk/.vtp files
system([ openFASTexe ' -VTKLin ElastoDyn-Modes.viz']);

% visualize with ParaView, saving as avi files
system( 'set path=C:\Program Files\ParaView 5.7.0-Windows-Python3.7-msvc2015-64bit\bin;%path% && pvpython plotModeShapes.py')

% convert avi to gif files and fix issue with pvpython not saving the
% correct frame rate in the avi file (was an issue in 5.5, but appears to be
% fixed in 5.7)
for i=1:15
    fileName = [RootName 'Mode' num2str(i) '.LinTime1'];
    avi2gif( [fileName '.avi'], [fileName '.gif'], 1, 30 );
end

return;

%% ------------------------------------------------------------
[Campbell] = runCampbell(RootName, MBC);


%% ------------------------------------------------------------
function [Campbell] = runCampbell(RootName, MBC)

    fst_file = [RootName 'fst'];
    [BladeLen, TowerLen] = getLengths(fst_file);
    
    Campbell = campbell_diagram_data(MBC, BladeLen, TowerLen);

return;
end


%% ------------------------------------------------------------
function [BladeLen, TowerLen] = getLengths(fst_file)

    FP = FAST2Matlab(fst_file,2);
    EP = GetFASTPar_Subfile(FP, 'EDFile', '.', '.');
    
    TipRad = GetFASTPar(EP, 'TipRad');
    HubRad = GetFASTPar(EP, 'HubRad');
    
    BladeLen  = TipRad - HubRad;
    TowerLen = GetFASTPar(EP, 'TowerHt');

return;
end