%%
caseFile = './glue-codes/fast/CaseList.md';
[pathstr] = fileparts(caseFile);

fid = fopen(caseFile);
caseNames = textscan(fid,'%s');
caseNames = caseNames{1};
fclose(fid);

for i= 1:length(caseNames)
    casePath = [ pathstr filesep caseNames{i} ];
    ConvertFAST8_16to17( [casePath filesep caseNames{i} '.fst'], casePath );
end

%%
caseFile = './modules-local/beamdyn/CaseList.md';
[pathstr] = fileparts(caseFile);

fid = fopen(caseFile);
caseNames = textscan(fid,'%s');
caseNames = caseNames{1};
fclose(fid);

for i= 1:length(caseNames)
    casePath = [ pathstr filesep caseNames{i} ];
    ConvertBeamDynDriver( [casePath filesep 'bd_driver.inp'], casePath );  
end
