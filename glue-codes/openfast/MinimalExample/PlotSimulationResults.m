%% Documentation   
% Standalone script to read an ASCII OpenFAST output and plot some channels.
%
% Contact: E. Branlard 

%% Initialization
clear all; close all; clc; % addpath(genpath('PATH/TO/matlab-toolbox'))

%% Parameters
outfile      = 'Main.out';
plotChannels = {'OoPDefl1','IPDefl1','TTDspFA','TTDspSS'};

%% Read out file
% NOTE: it's best to use ReadFASTtext.m from the matlab-toolbox instead:
%    [data, channels, units, headers] = ReadFASTtext(outfile);
fid = fopen(outfile);
for i = 1:6; l=fgetl(fid); end % Read header
channels = textscan(fgetl(fid), '%s'){1,1}; % Channel names
units    = textscan(fgetl(fid), '%s'){1,1}; % Channel units
data     = cell2mat( textscan( fid, repmat(' %f',1,length(channels)))); % Actual data
fclose(fid);
disp('Available channels:')
disp(channels)

%% Plot list of selected channels
nPlots = length(plotChannels);
time = data(:,1);
figure()
for ip = 1:nPlots
    % Find index of plot channel within data
    id = find(ismember(channels,plotChannels{ip}));
    subplot(nPlots, 1, ip);
    plot(time, data(:,id))
    xlabel('Time (s)')
    ylabel([channels{id} ' ' units{id}])
end


