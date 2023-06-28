""" 

Perform numerical integration of the TailFin 1DOF model.
See README.md

"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# Welib https://github.com/ebranlard/welib
import welib.weio as weio
from welib.system.mech_system import MechSystem
from welib.system.statespacelinear import LinearStateSpace


# --- Parameters defining the system and simulation
# Aero params
U0          = 10      # Wind speed [m/s]
d           = 10      # Distance between the yawing axis to the tailfin ref point/aerodynamic center [m]
Clalpha     = 2*np.pi  # Slope of the lift coefficient [-]
Area        = 1       # Area of the tailfin [m^2]
rho         = 1.225   # Air density [kg/m^3]
# Mech params
J  = 30000   # Total inertia of the tailfin  [kg m^2]
fastOut = 'Tailfin_FreeYaw1DOF_PolarBased.outb'

# --- Derived parameters
K_lin = 1/2*rho*U0**2*Area*Clalpha*d        # x theta
D_lin = 1/2*rho*U0**2*Area*Clalpha*d*(d/U0) # x theta_dot

# --- Read OpenFAST outputs, use them for initial condition and time vector
dfOF = weio.read(fastOut).toDataFrame()
theta0      = dfOF['Q_TFrl_[rad]'].values[0]
thetadot0   = dfOF['QD_TFrl_[rad/s]'].values[0]
time = np.linspace(0,dfOF['Time_[s]'].values[-1],2000)


# --- External aerodynamic force
def Faero(t, q, qdot, calcOutput=False):
    theta     = q[0]
    theta_dot = qdot[0]
    Vrel_r    = U0*np.cos(theta)
    Vrel_t    = - U0*np.sin(theta) -theta_dot*d
    alpha     = np.arctan2(Vrel_t, Vrel_r)
    alpha_lin = -theta -theta_dot*d/U0
    Vrel_n2   = Vrel_r**2 + Vrel_t**2
    L =  1/2*rho * Area * Vrel_n2 * Clalpha * alpha # NL
    #L =  1/2*rho * Area * Vrel_n2 * Clalpha * alpha_lin 
    #L =  1/2*rho * Area * U0**2 * Clalpha * alpha_lin
    M = d * L * np.cos(alpha)
    #M = d * L 
    if not calcOutput:
        return M
    else:
        return pd.Series({'alpha [deg]':alpha*180/np.pi, 'Vrel [m/s]':np.sqrt(Vrel_n2)}) #,'L':L,'M':M})

# --- Setup a Mechanical system object, to easily integrate
sys= MechSystem(M=J) #, C=c, K=k)
# sys.setForceTimeSeries(time,F)
sys.setInitialConditions([theta0],[thetadot0])
sys.setForceFunction(Faero)
sys.setOutputFunction(lambda t,q,qd: Faero(t,q,qd, calcOutput=True))
print(sys)
res, dfnl = sys.integrate(time, method='LSODA', calc='xdd,f,y')
#df = sys.res2DataFrame(sStates=['Q_TFrl','QD_TFrl'], calc='xdd,f,y', Factors=[180/np.pi]) #, x0=None, xd0=None,sAcc=None, sForcing=None)


# --- Do the same with the linear state space class
A=np.zeros((2,2))
A[0,1]=1
A[1,0]=-1/J*K_lin
A[1,1]=-1/J*D_lin
print('K_lin',K_lin)
print('D_lin',D_lin)
sysl = LinearStateSpace(A=A)
sysl.setStateInitialConditions([theta0,thetadot0])
# sysl.setInputTimeSeries(time,F)
print(sysl)
resln, dfln = sysl.integrate(time, method='LSODA', calc='y')

# --- Plot States
# Nonlinear model
axes = sys.plot(label='Python')
# OF
axes[0].plot(dfOF['Time_[s]'],dfOF['Q_TFrl_[rad]']   ,'k:', label='OpenFAST')
axes[1].plot(dfOF['Time_[s]'],dfOF['QD_TFrl_[rad/s]'],'k:', label='OpenFAST')
# Linear model
sysl.plot_states(axes=axes, label='Linear model', ls='--')
axes[0].set_ylabel('Q TFrl [rad]')
axes[1].set_ylabel('QD TFrl [rad/s]')
axes[0].get_figure().savefig('_Tailfin_ComparisonStates.png')

# --- Plot Misc outputs
# Nonlinear model
axes = sys.plot_outputs(label='Python nonlinear')
axes[0].plot(dfOF['Time_[s]'],dfOF['TFAlpha_[deg]']  ,'k:', label='OpenFAST')
axes[0].legend()
axes[1].plot(dfOF['Time_[s]'],dfOF['TFVrel_[m/s]']   ,'k:', label='OpenFAST')
axes[0].get_figure().savefig('_Tailfin_ComparisonOutputs.png')

plt.show()
