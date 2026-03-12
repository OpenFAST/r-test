## 5MW_MRSemi_DLL_WSt_WavesIrr

Example of a twin-rotor semi-submersible with a shared flexible substructure.

<img width="1200" height="800" alt="5MW_MRSemi_DLL_WSt_WavesIrr" src="https://github.com/user-attachments/assets/cf81e7a7-b5aa-45b3-a3ac-ceb642971bfa" />

The animation 5MW_MRSemi_DLL_WSt_WavesIrr.mp4 visualizes approximately the first 96 sec of the simulation. 

The VTK data for the animation was generated using the following settings:

```
---------------------- VISUALIZATION ------------------------------------------
          2   WrVTK           - VTK visualization data output: (switch) {0=none; 1=initialization data only; 2=animation; 3=mode shapes}
          1   VTK_type        - Type of VTK visualization data: (switch) {1=surfaces; 2=basic meshes (lines/points); 3=all meshes (debug)} [unused if WrVTK=0]
false         VTK_fields      - Write mesh fields to VTK data files? (flag) {true/false} [unused if WrVTK=0]
          5   VTK_fps         - Frame rate for VTK output (frames per second){will use closest integer multiple of DT} [used only if WrVTK=2 or WrVTK=3]
```

The VTK data was generated at 5 fps. The animation is played at 30 fps, resulting in a 6x speed up compared to real time.

Reference:

- Wang, L., Jonkman, J., Slaughter, D., Platt, A., Wiley, W., and Ross, H. (2025), OpenFAST development for improved hydro-elastics of multi-member support structures [presentation], NAWEA/WindTech 2025, Richardson, TX, October 15-17.
