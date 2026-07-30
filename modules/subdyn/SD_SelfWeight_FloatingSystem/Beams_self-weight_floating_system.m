clear; clc; close all

% MATLAB script to plot the shear forces, axial forces, and bending
% moments of a cantilever beam with 2 members and one concentrated mass.
%
% The system experiences rigid body motion replicating a floating system.
% While the system reorients in space, the self-weight is projected onto the
% local beam coordinate system accordingly.
%
% Schematic representation:
%       _ _ _ _ _ _ _ _ _ _
%      |         |         |
%      *  Beam 1 *  Beam 2 *----*
%      |_ _ _ _ _|_ _ _ _ _|
%     J1         J2       J3    J4
%      --->
%      L
%

%% System properties:

% Hollow circular cross-section geometry:
D   = 5;      % Outer diameter [m]
t   = 0.1;    % Wall thickness [m]

% Material properties:
rho = 7860;   % Density [kg/m^3]

% Points of interest along the beam (tip = L(end) = 10 m):
L = [0 2.5 5 7.5 10]; % Positions [m]

% Concentrated tip mass and its eccentricity from beam tip:
m = 2000;  % Mass [kg]
d = 1;     % Eccentricity of mass from beam tip [m]

%% Boundary conditions:
% The system starts horizontal (0 deg) and rotates to vertical (-90 deg)
% over 90 seconds at a constant rate of 1 deg/s.
% This follows the OpenFAST global coordinate convention:
% rotation of -90 deg around the y-axis.
angle = linspace(0,-90,91); % Angular position [deg]
angle = deg2rad(angle);     % Angular position [rad]

% Gravity acceleration:
g = 9.80665; % Gravity along -z direction [m/s^2]

%% Computing the analytical solution:

% Beam self-weight (uniformly distributed load)
% Cross-sectional area of hollow circular section [m^2]:
A = pi*((D/2)^2-((D/2)-t)^2);

% Self-weight per unit length [N/m]:
w = rho*A*g;

% Distance from each point to the beam tip [m]:
dL = L(end) - L';

% Shear force:
% Contributions: tip mass weight + distributed weight of remaining beam,
% projected onto the transverse beam axis via cos(angle).
F_shear = (m*g + w*dL).*cos(angle); % [N]
F_shear = F_shear/1E3;              % [N] -> [kN]

% Axial force:
% Same resultant as shear but projected onto the beam longitudinal axis
% via sin(angle).
F_axial = (m*g + w*dL).*sin(angle);  % [N]
F_axial = F_axial/1E3;               % [N] -> [kN]

% Bending moment:
% Contributions:
%   - Tip mass (with eccentricity d) acting at lever arm (dL + d)
%   - Distributed load with centroid at dL/2 from each section
% Projected onto the transverse beam axis via cos(angle).
M_bending = -(m*g*(dL + d) + w*dL.^2/2).*cos(angle);  % [Nm]
M_bending = M_bending/1E3;                            % [Nm] -> [kNm]

% Saving the results in a 3D matrix:
% F(i, j, k):
%   i = spatial index (1..5, corresponding to positions in L)
%   j = time/angle index (1..91, corresponding to angles in 'angle')
%   k = load type: 1 = Shear [kN], 2 = Axial [kN], 3 = Bending [kNm]

F = cat(3, F_shear, F_axial, M_bending);  % [5 x 91 x 3]

% Label mapping for reference:
% F(:,:,1) -> Shear force     [kN]
% F(:,:,2) -> Axial force     [kN]
% F(:,:,3) -> Bending moment  [kNm]

%% Plotting the solution:
figure('color','w')
y_label = {'Shear force [kN]', 'Axial force [kN]', 'Bending Moment [kNm]'};
c = 1; % Counter
for j = 1:3 % Going through the shear force, axial force, and bending moments
    for i = 1:5
        subplot(3,5,c) % Going through the 5 locations of interest

        % Magnitude of interest:
        plot(rad2deg(angle), F(i,:,j), 'k', 'LineWidth', 1.25)

        grid on
        xlabel('Y-global rotation [deg]')
        xlim([-90 0])
        set(gca, 'XTick',-90:30:0)
        ylabel(y_label{j})

        if j == 1
            if i == 1 || i == 3 || i == 5
                title(['L = ', num2str(L(i)), ' m. End node'])
            elseif i == 2 || i == 4
                title(['L = ', num2str(L(i)), ' m. Interior node'])
            end
        end

        c = c+1;
    end
end