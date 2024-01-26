clear; clc; close all

% MATLAB script to create a cantilever beam with 2 members.
% Created by: R. Bergua @ National Renewable Energy Laboratory
% Date: 11/27/2023 (mm/dd/yyyy)
%
% The Timoshenko beam formulation is available here: 
% https://openfast.readthedocs.io/en/main/source/user/subdyn/theory.html#beam-element-formulation
%
% Schematic representation of the finite element model:
%
%                    ----*----  Node 3
%                   |          |
%                   |  Beam 2  |
%                   |          |
%        Z           ----*----  Node 2
%        ^          |          |
%        |          |  Beam 1  |
%        |          |          |
%        |---> X     ----*----  Node 1
%
% 

%% Material definition:
E =  210E9; % Young Modulus [N/m^2].   
rho = 7860; % Material density [kg/m^3].
v = 0.3; % Poisson ratio [-].

%% Geometrical dimensions:
beam_dimensions = [0 1 0.95;           % Height = 0 m, External diameter = 1 m, Internal diameter = 1-(2*0.025) m
                   5 1 0.95;           % Height = 5 m, External diameter = 1 m, Internal diameter = 1-(2*0.025) m
                  10 1 0.95];          % Height = 10 m, External diameter = 1 m, Internal diameter = 1-(2*0.025) m
 
%% External forces:
forces = [10 1 2E6];                  % Height = 10 m, direction 1 = X, magnitude = 2E6 N
      
%% Properties of the system:
nodes = length(beam_dimensions);  % Number of nodes in the system.
DOFs = nodes*6; % Each node has 6 degrees of freedom: 3 translations and 3 rotations.
beam_elements = length(beam_dimensions)-1;

%% Calculating the lenght of the different beams and the sectional properties of the beam:
% Initializing the variables:
beams_height = zeros(beam_elements,1);
beams_ext_diameter = zeros(beam_elements,1); 
beams_int_diameter = zeros(beam_elements,1); 
for i = 1:beam_elements
    beams_height(i) = beam_dimensions(i+1,1)-beam_dimensions(i,1);
    beams_ext_diameter(i) = (beam_dimensions(i+1,2)+beam_dimensions(i,2))/2;
    beams_int_diameter(i) = (beam_dimensions(i+1,3)+beam_dimensions(i,3))/2;
end

%% Cross section properties: 
% Initializing the variables:
A = zeros(beam_elements,1);
Jx = zeros(beam_elements,1);
Jy = zeros(beam_elements,1);
Jz = zeros(beam_elements,1);
for i = 1:beam_elements
    A(i) = pi*((beams_ext_diameter(i)/2)^2-(beams_int_diameter(i)/2)^2);       % Area [m^2]
    % Second Moment of Area [m^4]:
    Jx(i) = (pi/4)*((beams_ext_diameter(i)/2)^4-(beams_int_diameter(i)/2)^4);  % With respect to principal axes X.
    Jy(i) = Jx(i);                        % With respect to principal axes Y.
    Jz(i) = (pi/2)*((beams_ext_diameter(i)/2)^4-(beams_int_diameter(i)/2)^4);  % With respect to principal axes Z (longitudinal along beam).
end  

%% Element stiffness matrix (12DOFs):
% Stiffness for each element: 1 element, 2 nodes.

% Shear Modulus calculation:
G = E/(2*(1+v));   % Shear Modulus [N/m^2]

% Shear correction factors (K_sx, K_sy):
% Initializing the variables:
K_sx = zeros(beam_elements,1);
K_sy = zeros(beam_elements,1);
% Shear correction factor for the Timoshenko formulation:
% Initializing the variables:
k_ax = zeros(beam_elements,1);
k_ay = zeros(beam_elements,1);
A_sx = zeros(beam_elements,1);
A_sy = zeros(beam_elements,1);
for i = 1:beam_elements 
    % k_ax and k_ay for hollow circular cross sections:
    k_ax(i) = (6*((1+v)^2)*(1+(beams_int_diameter(i)/beams_ext_diameter(i))^2)^2)/(((1+(beams_int_diameter(i)/beams_ext_diameter(i))^2)^2)*(7+14*v+8*v^2)+((4*(beams_int_diameter(i)/beams_ext_diameter(i))^2)*(5+10*v+4*v^2)));
    k_ay(i) = k_ax(i); 
    % Shear areas (A_sx, A_sy) along the local x and y (principal) axes.
    A_sx(i) = k_ax(i)*A(i);
    A_sy(i) = k_ay(i)*A(i);
    % Shear correction factors:
    K_sx(i) = 12*E*Jy(i)/(G*A_sx(i)*(beams_height(i))^2);
    K_sy(i) = 12*E*Jx(i)/(G*A_sy(i)*(beams_height(i))^2);
end

% Changing the variables name for convenience:
L_e = beams_height;

% Initializing the element stiffness matrices:
Ke = zeros(12,12,beam_elements);

for i = 1:beam_elements
    Ke(:,:,i) = [12*E*Jy(i)/((L_e(i)^3)*(1+K_sy(i)))                0                                   0                            0                          6*E*Jy(i)/((L_e(i)^2)*(1+K_sy(i)))              0       -12*E*Jy(i)/((L_e(i)^3)*(1+K_sy(i)))                    0                               0                               0                       6*E*Jy(i)/((L_e(i)^2)*(1+K_sy(i)))          0           ;...
                                0                       12*E*Jx(i)/((L_e(i)^3)*(1+K_sx(i)))             0           -6*E*Jx(i)/((L_e(i)^2)*(1+K_sx(i)))                         0                               0                           0                   -12*E*Jx(i)/((L_e(i)^3)*(1+K_sx(i)))            0           -6*E*Jx(i)/((L_e(i)^2)*(1+K_sx(i)))                         0                           0           ;...              
                                0                                   0                             E*A(i)/L_e(i)                      0                                          0                               0                           0                                   0                         -E*A(i)/L_e(i)                        0                                       0                           0           ;...
                                0                       -6*E*Jx(i)/((L_e(i)^2)*(1+K_sx(i)))             0           (4+K_sx(i))*E*Jx(i)/(L_e(i)*(1+K_sx(i)))                    0                               0                           0                     6*E*Jx(i)/((L_e(i)^2)*(1+K_sx(i)))            0         (2-K_sx(i))*E*Jx(i)/(L_e(i)*(1+K_sx(i)))                      0                           0           ;...
                  6*E*Jy(i)/((L_e(i)^2)*(1+K_sy(i)))                0                                   0                            0                         (4+K_sy(i))*E*Jy(i)/(L_e(i)*(1+K_sy(i)))         0        -6*E*Jy(i)/((L_e(i)^2)*(1+K_sy(i)))                    0                               0                               0                     (2-K_sy(i))*E*Jy(i)/(L_e(i)*(1+K_sy(i)))      0           ;...
                                0                                   0                                   0                            0                                          0                         G*Jz(i)/L_e(i)                    0                                   0                               0                               0                                       0                     -G*Jz(i)/L_e(i)   ;...
                -12*E*Jy(i)/((L_e(i)^3)*(1+K_sy(i)))                0                                   0                            0                           -6*E*Jy(i)/((L_e(i)^2)*(1+K_sy(i)))            0         12*E*Jy(i)/((L_e(i)^3)*(1+K_sy(i)))                   0                               0                               0                       -6*E*Jy(i)/((L_e(i)^2)*(1+K_sy(i)))         0           ;...
                                0                      -12*E*Jx(i)/((L_e(i)^3)*(1+K_sx(i)))             0             6*E*Jx(i)/((L_e(i)^2)*(1+K_sx(i)))                        0                               0                           0                    12*E*Jx(i)/((L_e(i)^3)*(1+K_sx(i)))            0            6*E*Jx(i)/((L_e(i)^2)*(1+K_sx(i)))                         0                           0           ;...
                                0                                   0                             -E*A(i)/L_e(i)                     0                                          0                               0                           0                                   0                           E*A(i)/L_e(i)                       0                                       0                           0           ;...    
                                0                       -6*E*Jx(i)/((L_e(i)^2)*(1+K_sx(i)))             0           (2-K_sx(i))*E*Jx(i)/(L_e(i)*(1+K_sx(i)))                    0                               0                           0                     6*E*Jx(i)/((L_e(i)^2)*(1+K_sx(i)))            0         (4+K_sx(i))*E*Jx(i)/(L_e(i)*(1+K_sx(i)))                      0                           0           ;...      
                6*E*Jy(i)/((L_e(i)^2)*(1+K_sy(i)))                  0                                   0                            0                           (2-K_sy(i))*E*Jy(i)/(L_e(i)*(1+K_sy(i)))       0         -6*E*Jy(i)/((L_e(i)^2)*(1+K_sy(i)))                   0                               0                               0                      (4+K_sy(i))*E*Jy(i)/(L_e(i)*(1+K_sy(i)))     0           ;... 
                                0                                   0                                   0                            0                                          0                        -G*Jz(i)/L_e(i)                    0                                   0                               0                               0                                       0                      G*Jz(i)/L_e(i)  ];
end

%% Global stiffness matrix:
K = zeros(6*(nodes),6*(nodes)); % Initializing the matrix with the proper size

% Assembling the elements:
for i = 1:beam_elements
    K((6*i)-5:(i+1)*6,(6*i)-5:(i+1)*6)=Ke(:,:,i)+K((6*i)-5:(i+1)*6,(6*i)-5:(i+1)*6);
end

%% Element mass matrix (12DOFs):

% Initializing the element mass matrices:
Me = zeros(12,12,beam_elements);

for i = 1:beam_elements
    Me(:,:,i) = rho*[(13*A(i)*L_e(i)/35)+(6*Jy(i)/(5*L_e(i)))                     0                                 0                           0                           ((11*A(i)*L_e(i)^2)/210)+(Jy(i)/10)             0           ((9*A(i)*L_e(i))/70)-(6*Jy(i)/(5*L_e(i)))                       0                                0                          0                           -((13*A(i)*L_e(i)^2)/420)+(Jy(i)/10)                0       ;
                                        0                       (13*A(i)*L_e(i)/35)+(6*Jx(i)/(5*L_e(i)))            0           -((11*A(i)*L_e(i)^2)/210)-(Jx(i)/10)                        0                               0                               0                           ((9*A(i)*L_e(i))/70)-(6*Jx(i)/(5*L_e(i)))        0              ((13*A(i)*L_e(i)^2)/420)-(Jx(i)/10)                         0                               0       ;              
                                        0                                         0                          A(i)*L_e(i)/3                      0                                           0                               0                               0                                           0                           A(i)*L_e(i)/6                   0                                               0                               0       ;
                                        0                         -((11*A(i)*L_e(i)^2)/210)-(Jx(i)/10)              0          ((A(i)*L_e(i)^3)/105)+(2*L_e(i)*Jx(i)/15)                    0                               0                               0                           -((13*A(i)*L_e(i)^2)/420)+(Jx(i)/10)             0           -((A(i)*L_e(i)^3)/140)-(L_e(i)*Jx(i)/30)                       0                               0       ;
                      ((11*A(i)*L_e(i)^2)/210)+(Jy(i)/10)                         0                                 0                           0                         ((A(i)*L_e(i)^3)/105)+(2*L_e(i)*Jy(i)/15)         0               ((13*A(i)*L_e(i)^2)/420)-(Jy(i)/10)                         0                                0                          0                               -((A(i)*L_e(i)^3)/140)-(L_e(i)*Jy(i)/30)        0       ;
                                        0                                         0                                 0                           0                                           0                         Jz(i)*L_e(i)/3                        0                                           0                                0                          0                                               0                       Jz(i)*L_e(i)/6  ;
                     ((9*A(i)*L_e(i))/70)-(6*Jy(i)/(5*L_e(i)))                    0                                 0                           0                           ((13*A(i)*L_e(i)^2)/420)-(Jy(i)/10)             0            ((13*A(i)*L_e(i))/35)+(6*Jy(i)/(5*L_e(i)))                     0                                0                          0                           -((11*A(i)*L_e(i)^2)/210)-(Jy(i)/10)                0       ;
                                        0                       ((9*A(i)*L_e(i))/70)-(6*Jx(i)/(5*L_e(i)))           0           -((13*A(i)*L_e(i)^2)/420)+(Jx(i)/10)                        0                               0                               0                           ((13*A(i)*L_e(i))/35)+(6*Jx(i)/(5*L_e(i)))       0              ((11*A(i)*L_e(i)^2)/210)+(Jx(i)/10)                         0                               0       ;
                                        0                                         0                          A(i)*L_e(i)/6                      0                                           0                               0                               0                                           0                           A(i)*L_e(i)/3                   0                                               0                               0       ;    
                                        0                          ((13*A(i)*L_e(i)^2)/420)-(Jx(i)/10)              0         -((A(i)*L_e(i)^3)/140)-(L_e(i)*Jx(i)/30)                      0                               0                               0                           ((11*A(i)*L_e(i)^2)/210)+(Jx(i)/10)              0          ((A(i)*L_e(i)^3)/105)+(2*L_e(i)*Jx(i)/15)                       0                               0       ;      
                       -((13*A(i)*L_e(i)^2)/420)+(Jy(i)/10)                       0                                 0                           0                        -((A(i)*L_e(i)^3)/140)-(L_e(i)*Jy(i)/30)           0              -((11*A(i)*L_e(i)^2)/210)-(Jy(i)/10)                         0                                0                          0                               ((A(i)*L_e(i)^3)/105)+(2*L_e(i)*Jy(i)/15)       0       ; 
                                        0                                         0                                 0                           0                                           0                          Jz(i)*L_e(i)/6                       0                                           0                                0                          0                                               0                      Jz(i)*L_e(i)/3  ];
end

%% Global mass matrix:
% The global mass matrix will have the same dimensions as the global
% stiffness matrix:
M = zeros(6*(nodes),6*(nodes)); % Initializing the matrix
% Assembling the mass matrix: 
for i = 1:beam_elements
    M((6*i)-5:(i+1)*6,(6*i)-5:(i+1)*6)=Me(:,:,i)+M((6*i)-5:(i+1)*6,(6*i)-5:(i+1)*6);
end

%% Boundary conditions:
% Forces:
F = zeros(6*nodes,1);   % Initializing the force vector

% Converting from force at a given height [m] to node number in the FEM. 
% Adding this info as the 4th column of forces matrix:
for i = 1:length(forces(:,1))
    forces(i,4) = find(forces(i,1) == beam_dimensions(:,1));
end   

for i = 1:length(forces(:,1))
    F((forces(i,4)-1)*6+forces(i,2)) = forces(i,3);   % forces(i,4) indicates the node in the system matrix, forces(i,2) indicates the direction and forces(i,3) the magnitude.
end

% Clamp at node 1:
% Removing the DOFs from node 1 (first 6 rows and columns in mass and
% stiffness matrix and first 6 positions in force vector F):
K = K(7:end,7:end);
M = M(7:end,7:end);
F = F(7:end);

%% Solving the system from a static point of view:
d = K\F;

dx = d(1:6:length(d(:,1))); % Deflections in X direction [m] from bottom to top
dy = d(2:6:length(d(:,1))); % Deflections in Y direction [m] from bottom to top
dz = d(3:6:length(d(:,1))); % Deflections in Z direction [m] from bottom to top
Rx = d(4:6:length(d(:,1))); % Rotations around X [rad] from bottom to top
Ry = d(5:6:length(d(:,1))); % Rotations around Y [rad] from bottom to top
Rz = d(6:6:length(d(:,1))); % Rotations around Z [rad] from bottom to top

deflections = [dx dy dz Rx Ry Rz]; % Deflections from bottom to top