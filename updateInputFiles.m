%% example files in the OpenFAST glue-code regression tests:
caseFile = './glue-codes/openfast/CaseList.md';
[pathstr] = fileparts(caseFile);

fid = fopen(caseFile);
caseNames = textscan(fid,'%s');
caseNames = caseNames{1};
fclose(fid);

for i= 1:length(caseNames)
    casePath = [ pathstr filesep caseNames{i} ];
    ConvertFAST8_16to17( [casePath filesep caseNames{i} '.fst'], casePath );
end


%% example files in the OpenFAST BeamDyn regression tests:
caseFile = './modules/beamdyn/CaseList.md';
[pathstr] = fileparts(caseFile);

fid = fopen(caseFile);
caseNames = textscan(fid,'%s');
caseNames = caseNames{1};
fclose(fid);

for i= 1:length(caseNames)
    casePath = [ pathstr filesep caseNames{i} ];
    ConvertBeamDynDriver( [casePath filesep 'bd_driver.inp'], casePath );  
end


%% example files in the OpenFAST BeamDyn documentation:
docsPath = '../../docs/source/user/beamdyn/examples/';
caseNames = strcat(docsPath, {'bd_driver_dynamic_nrel_5mw.inp', 'bd_driver_static_nrel_5mw.inp'} );

for i= 1:length(caseNames)
    ConvertBeamDynDriver( caseNames{i}, docsPath );  
end


%% example files in the OpenFAST AeroDyn documentation:
docsPath = '../../docs/source/user/aerodyn/examples/';
caseNames = strcat(docsPath, {'ad_driver_example.inp'} );

for i= 1:length(caseNames)
    ConvertAeroDynDriver( caseNames{i}, docsPath );  
end

%% example files in the OpenFAST AeroDyn regression tests:
caseFile = './modules/aerodyn/CaseList.md';
[pathstr] = fileparts(caseFile);

fid = fopen(caseFile);
if fid > 0
    caseNames = textscan(fid,'%s');
    caseNames = caseNames{1};
    fclose(fid);

    for i= 1:length(caseNames)
        casePath = [ pathstr filesep caseNames{i} ];
        ConvertAeroDynDriver( [casePath filesep 'ad_driver.inp'], casePath );  
    end
end


