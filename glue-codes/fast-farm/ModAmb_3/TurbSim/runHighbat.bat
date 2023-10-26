@echo off
set nTurbines=4

for /L %%n in (1,1,%nTurbines%) do (
        start "" /B cmd /C D:\data\40_mahfouz\bin\TurbSim\TurbSim.exe D:\data\40_mahfouz\github\repo\r-test\glue-codes\fast-farm\ModAmb_3\Cond00_v08.0_PL0.2_TI6\Case0_wdir0.0\Seed_0\TurbSim\HighT%%n.inp > D:\data\40_mahfouz\github\repo\r-test\glue-codes\fast-farm\ModAmb_3\Cond00_v08.0_PL0.2_TI6\Case0_wdir0.0\Seed_0\TurbSim\log.hight%%n.seed0.txt 2>&1
)

echo Script execution completed
