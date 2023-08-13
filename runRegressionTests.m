pathToLocalFiles = '..\..\build\reg_tests';
% pathToNewFiles = '.\';
OpenFASTexe = '..\..\build\bin\openfast_x64_Double.exe';


%% example files in the OpenFAST glue-code regression tests:
caseFile = './glue-codes/openfast/CaseList.md';
[pathstr] = fileparts(caseFile);
LocalPath = fullfile(pathToLocalFiles, pathstr);


fid = fopen(caseFile);
caseNames = textscan(fid,'%s');
caseNames = caseNames{1};
fclose(fid);

for i= 1:length(caseNames)
    baselineRoot = fullfile(pathstr,   caseNames{i}, caseNames{i});
    localRoot    = fullfile(LocalPath, caseNames{i}, caseNames{i});
    
    status = system([OpenFASTexe ' ' localRoot '.fst']);
    if status ~= 0
        disp(['case failed: ' newRoot])
    else
        PlotFASToutput(strcat({baselineRoot,localRoot},'.outb'),{baselineRoot,localRoot},2);
    end
end


% %% example files in the OpenFAST BeamDyn regression tests:
% caseFile = './modules/beamdyn/CaseList.md';
% [pathstr] = fileparts(caseFile);
% 
% fid = fopen(caseFile);
% caseNames = textscan(fid,'%s');
% caseNames = caseNames{1};
% fclose(fid);
% 
% for i= 1:length(caseNames)
%     casePath = [ pathstr filesep caseNames{i} ];
%     ConvertBeamDynDriver( [casePath filesep 'bd_driver.inp'], casePath );  
% end

%%
pathstr = './modules/hydrodyn/';

caseNames = GetSubDirsFirstLevelOnly(pathstr);
HDexe= '..\..\build\bin\HydroDynDriver_x64.exe';

for i= 4 %1:length(caseNames)
    if ~contains(caseNames{i},'py_')
        % skip the python ones for now
    
        casePath = [ pathstr filesep caseNames{i} ];
        
        baselineRoot = casePath;
        localRoot = fullfile(pathToLocalFiles, casePath);
    
        status = system([HDexe ' ' casePath filesep 'hd_driver.inp']);
        if status ~= 0
            disp(['case failed: ' casePath])
        else
            PlotFASToutput(strcat({baselineRoot,localRoot},filesep, 'driver.out'),{'baseline','local'},2);
        end
    end
end

% executeHydrodynRegressionCase.py -p=true -v=true %caseName%  HDexe C:\Users\bonnie.jonkman\Documents\Data\Software\Code\openfast\ C:\Users\bonnie.jonkman\Documents\Data\Software\Code\openfast\build\reg_tests\modules\hydrodyn\ 1e-5 Windows Intel