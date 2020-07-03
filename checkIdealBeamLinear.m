%
% by Bonnie Jonkman
% (c) 2018 Envision Energy, USA
%--------------------------------------------------------------------------

%% let's get the directory that contains the template files
if ispc
    FASTexe = '..\..\..\bin\enFAST_Win32.exe';
else %ismac || isunix
    error('set name/location of FAST executable')
end

FST_files = {'./glue-codes/openfast/Ideal_Beam_Fixed_Free_Linear/Ideal_Beam_Fixed_Free_Linear.fst', ...
             './glue-codes/openfast/Ideal_Beam_Free_Free_Linear/Ideal_Beam_Free_Free_Linear.fst'};

orders = 8; %3:12;
nPoints = length(FST_files);
nOrder  = max(orders);

FAST_linData = cell(nPoints,1); % raw data read from FAST's .lin files
getMatData   = cell(nPoints,nOrder); % FAST .lin data converted to format that MBC or eigensolver can process
CampbellData = cell(nPoints,nOrder);
ED_linData   = cell(nPoints,1);
BD_linData   = cell(nPoints,1);
BD_sumData   = cell(nPoints,1);
nf           = cell(nPoints,nOrder);


% we should get these from the BD and ED input files:
BladeLen = 100; %m
TowerLen = 5e-5; %m

% fixed-free beam:
AnalyticalResults{1} = [1.8751; 1.8751; 4.694; 4.694; 7.855; 7.855].^2 * sqrt(1037.13E9 / 9517.14 / 100^4) / 2/ pi;
% free-free beam:
AnalyticalResults{2} = [4.7300; 4.7300; 7.8532; 7.8532; 10.9956; 10.9956].^2 * sqrt(1037.13E9 / 9517.14 / 100^4) / 2/ pi;
% AnalyticalResults{2} = [3.717; 3.717; 10.247; 10.247];

% (1:nPoints)=FST_files full linearization; nPoints+(1:nPoints)=BD sum file
numModes = 3;
PlotVals.Modes           = zeros(nOrder,numModes,nPoints*2);
PlotVals.AnalyticalModes = zeros(nOrder,numModes,nPoints);

for i=1:nPoints
    for j=1:numModes
        PlotVals.AnalyticalModes(:,j,i) = AnalyticalResults{i}(2*j-1);
    end
end

osDesc = {'windows-intel', 'macos-gnu', 'linux-intel', 'linux-gnu'};

%%
% % % BDpar = FAST2Matlab('ideal-beam/BeamDyn.dat',2);
for i_order = orders
    
    for i_os = 1:length(osDesc)
        
        for i = 1:nPoints    
            FileRoot = strrep(FST_files{i}, '.fst','');

            FileRoot = strrep(FileRoot,'_Linear/Ideal_',['_Linear/' osDesc{i_os} '/Ideal_']);

            %%
        % % %     BD_sumData{i} = ReadBeamDynSummary( [FileRoot '.BD1.sum']);
            ED_linData{i} = ReadFASTLinear( [FileRoot '.1.ED.lin' ]);
            BD_linData{i} = ReadFASTLinear( [FileRoot '.1.BD1.lin']);

            [getMatData{i,i_order}, FAST_linData{i}] = fx_getMats( [FileRoot '.1.lin'] );
            getMatData{i,i_order}.eigSol = eiganalysis(getMatData{i,i_order}.AvgA);
            getMatData{i,i_order}.performedTransformation = false;
            getMatData{i,i_order}.RotSpeed_rpm = 0;

            CampbellData{i,i_order} = campbell_diagram_data(getMatData{i,i_order}, BladeLen, TowerLen);

        end
%%

        fprintf('\n\n');
        fprintf('%s:\n', osDesc{i_os});
        fprintf('       Analytical     Linearization   BD Summary File\n')
        fprintf('----------------- ----------------- -----------------\n')
        i=1;
        fprintf('* Fixed-Free Beam:\n');

            % get values from BD summary file's reported K and M matrices:
        % % %     n=size(BD_sumData{i}.K,1) - 6;
        % % %     BD_sumData{i}.A = [zeros(n) eye(n); -BD_sumData{i}.M(7:end,7:end)\BD_sumData{i}.K(7:end,7:end) zeros(n)];
        % % %     BD_sumData{i}.eigSol = eiganalysis(BD_sumData{i}.A);
        % % %     nf{i,i_order} = sort(BD_sumData{i}.eigSol.NaturalFreqs_Hz);


            nSolutions = length(AnalyticalResults{i});
        % % %     fprintf( '%17.4f %17.4f %17.4f\n' , [ AnalyticalResults{i}, CampbellData{i,i_order}.NaturalFreq_Hz(1:nSolutions), nf{i,i_order}(1:nSolutions)]' );
            fprintf( '%17.4f %17.4f\n' , [ AnalyticalResults{i}, CampbellData{i,i_order}.NaturalFreq_Hz(1:nSolutions) ]');
            fprintf('     .............. # rigid body modes .............. \n');
        % % %     fprintf( '%17.0f %17.0f %17.0f\n\n' , [ 0, getMatData{i,i_order}.eigSol.NumRigidBodyModes, BD_sumData{i}.eigSol.NumRigidBodyModes] );
            fprintf( '%17.0f %17.0f\n\n' , [ 0, getMatData{i,i_order}.eigSol.NumRigidBodyModes] );

        i=2;
        fprintf('* Free-Free Beam:\n');
        % % %     n=size(BD_sumData{i}.K,1);
        % % %     BD_sumData{i}.A = [zeros(n) eye(n); -BD_sumData{i}.M\BD_sumData{i}.K zeros(n)];
        % % %     BD_sumData{i}.eigSol = eiganalysis(BD_sumData{i}.A);
        % % %     nf{i,i_order} = sort(BD_sumData{i}.eigSol.NaturalFreqs_Hz);

        % % %     indx = nf{i,i_order} < 0.1;
        % % %     NumRigidBodyModes = sum( indx );
        % % %     nf{i,i_order} = nf{i,i_order}( ~indx  );

            nSolutions = length(AnalyticalResults{i});
            %Note that I'm assuming the extra ridig-body modes show up as low
            %frequency modes. If that is not true, we should adjust the index into
            %CampbellData{i}.NaturalFreq_Hz below.

        % % %     fprintf( '%17.4f %17.4f  %17.4f\n' , [ AnalyticalResults{i}, ...
        % %         CampbellData{i,i_order}.NaturalFreq_Hz( (1:nSolutions)+max(0,6-getMatData{i,i_order}.eigSol.NumRigidBodyModes) ),  ...
        % %         nf{i,i_order}(1:nSolutions)]' );
            fprintf( '%17.4f %17.4f\n' , [ AnalyticalResults{i}, ...
                CampbellData{i,i_order}.NaturalFreq_Hz( (1:nSolutions)+max(0,6-getMatData{i,i_order}.eigSol.NumRigidBodyModes) )]');
            fprintf('     .............. # rigid body modes .............. \n');
        % % %     fprintf( '%17.0f %17.0f  %17.0f\n\n' , [ 6, getMatData{i,i_order}.eigSol.NumRigidBodyModes NumRigidBodyModes] );
            fprintf( '%17.0f %17.0f\n\n' , [ 6, getMatData{i,i_order}.eigSol.NumRigidBodyModes ] );

    end
end


