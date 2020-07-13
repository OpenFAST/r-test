pathToNewFiles = '..\..\build\reg_tests';
OpenFASTexe = '..\..\build\bin\openfast_Win32.exe';
goldStandard = 'windows-intel';


%% example files in the OpenFAST glue-code regression tests:
caseFile = './glue-codes/openfast/CaseList.md';
[pathstr] = fileparts(caseFile);
NewPath = fullfile(pathToNewFiles, pathstr);


fid = fopen(caseFile);
caseNames = textscan(fid,'%s');
caseNames = caseNames{1};
fclose(fid);

for i= 1:length(caseNames)
    oldRoot = fullfile(pathstr, caseNames{i}, goldStandard, caseNames{i});
    newRoot = fullfile(NewPath, caseNames{i}, caseNames{i});
    
    status = system([OpenFASTexe ' ' newRoot '.fst']);
    if status ~= 0
        disp(['case failed: ' newRoot])
    else
        PlotFASToutput(strcat({oldRoot,newRoot},'.outb'),{oldRoot,newRoot});
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

