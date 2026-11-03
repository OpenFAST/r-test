## MHK\_RM1\_Floating\_MR\_Linear

Test of features for floating multi-rotor MHK turbines

* Two floating MHK RM1 turbines (MHK = 2)
* FRM1 Quad floating platform (full SubDyn model)
* Full strip-theory HydroDyn model aligned with the SubDyn model mesh
* Consistent wave and current flow for mooring lines (SEASTATE WaterKin in MoorDyn)
* ElastoDyn, InflowWind, AeroDyn, HydroDyn, MoorDyn, SeaState, SubDyn
* Blade, tower, and platform DOFs on
* Fixed rotor rotational speeds
* Standard HAT geometry inputs
* Steady and uniform inflow (can use turbulent inflow if needed)
* Steady airfoil aerodynamics
* No cavitation check

MHK RM1 turbine based on the following reference:
Neary et al., "Methodology for Design and Economic Analysis of Marine Energy
Conversion (MEC) Technologies", Sandia Report SAND2014-9040, 2014.



For the hydrodynamic and structural model of the platform/support structure, cite

Wang, L., Jonkman, J., Tran, T.T., Ross, H., Platt, A., Slaughter, D., 2026,

Advancements in OpenFAST's modeling capabilities for marine turbines, presentation

at the UMERC+METS 2026 Conference, Hoboken, NJ, Aug. 4--6.

