% pathToNewFiles = '..\..\build\reg_tests';
pathToNewFiles = '.\';
OpenFASTexe = '..\..\build\bin\openfast_x64.exe';
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

%%

pathstr = './modules/hydrodyn/';

NewPath = pathstr;
goldStandard = 'windows-intel';

caseNames = GetSubDirsFirstLevelOnly(pathstr);
HDexe= '..\..\build\bin\HydroDynDriver_x64.exe';

for i= 1 %1:length(caseNames)
    casePath = [ pathstr filesep caseNames{i} ];
    
    if strcmpi(caseNames{i},'HydroDyn_NBodyMod_cases')
        caseNamesSub = GetSubDirsFirstLevelOnly(casePath);
        for j=1:length(caseNamesSub)
            casePathSub = [ casePath filesep caseNamesSub{j} ];
        
            oldRoot = fullfile(casePathSub, goldStandard);
        
            status = system([HDexe ' ' casePathSub filesep caseNamesSub{j} '.dvr']);
            if status ~= 0
                disp(['case failed: ' casePathSub])
            else
                PlotFASToutput(strcat({oldRoot,casePathSub},filesep, {[caseNamesSub{j} '.out'], [caseNamesSub{j} 'SEA.out']}),{oldRoot,casePathSub},2);
            end
        end
    else
        oldRoot = fullfile(casePath, goldStandard);
    
        status = system([HDexe ' ' casePath filesep 'hd_driver.inp']);
        if status ~= 0
            disp(['case failed: ' casePath])
        else
            PlotFASToutput(strcat({oldRoot,casePath},filesep, {'driver.HD.out','driver.SeaSt.out'}),{oldRoot,casePath},2);
        end
    end

end

% executeHydrodynRegressionCase.py -p=true -v=true %caseName%  HDexe C:\Users\bonnie.jonkman\Documents\Data\Software\Code\openfast\ C:\Users\bonnie.jonkman\Documents\Data\Software\Code\openfast\build\reg_tests\modules\hydrodyn\ 1e-5 Windows Intel