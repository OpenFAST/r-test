2023.04.07

This is a placeholder for testing the full-field wind box exceedance.  This is used for points requested by the LidarSim and OLAF modules.

The wind grid can be generated using the following commands.

- Windows:    `InflowWind_Driver.exe /BoxExceedAllow ifw_driver.inp`
- Linux/Mac:  `inflowwind_driver -BoxExceedAllow ifw_driver.inp`

This will produce a single time slice of YZ with extents beyond the edge of the wind file information.

The IPython notebook `IfW_CheckGrid.ipynb` can be used to visualized the wind (requires https://plotly.com/).
