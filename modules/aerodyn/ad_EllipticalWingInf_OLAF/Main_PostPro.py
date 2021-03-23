import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# Local 
import weio
import welib.fast.fastlib as fastlib


# --- Reference simulations OmniVor / AWSM
ref20 = weio.read('AnalyticalResults/Elliptic_NumReference20.csv').toDataFrame()
ref40 = weio.read('AnalyticalResults/Elliptic_NumReference40.csv').toDataFrame()
ref80 = weio.read('AnalyticalResults/Elliptic_NumReference80.csv').toDataFrame()

# --- OLAF
# _,sim20 = fastlib.spanwisePostPro('Main_EllipticalWing20.fst',avgMethod='constantwindow',avgParam=0.1,out_ext='.outb')
_,sim40,_,_ = fastlib.spanwisePostPro('Main_EllipticalWingInf_OLAF.dvr',avgMethod='constantwindow',avgParam=0.1,out_ext='.outb')
# _,sim80,_,_ = fastlib.spanwisePostPro('Main_EllipticalWing.fst',avgMethod='constantwindow',avgParam=0.1,out_ext='.outb')

# --- Theory
b         = 5
c0        = 1.0
V         = [1,0.1]
U0        = np.sqrt(V[0]**2 + V[1]**2)
alpha_rad = np.arctan2(V[1],V[0])
AR        = b*b/(np.pi*b*c0/4.)
CL_th     = 2.*np.pi*(alpha_rad)/(1.+2./AR);



# --- Plot
fig,ax = plt.subplots(1, 1, sharey=False, figsize=(6.4,4.8)) # (6.4,4.8)
fig.subplots_adjust(left=0.12, right=0.90, top=0.88, bottom=0.11, hspace=0.20, wspace=0.20)
ax.plot([-1,1], [CL_th, CL_th], 'k-', label ='Theory', lw=2)
# ax.plot((ref20['r/R_[-]']-0.5)*2 , ref20['Cl_[-]']  , '-' , label ='n=20')
ax.plot((ref40['r/R_[-]']-0.5)*2 , ref40['Cl_[-]']  , '-' , label ='n=40 (ref)')
# ax.plot((ref80['r/R_[-]']-0.5)*2 , ref80['Cl_[-]']  , '-' , label ='n=80 (ref)')
# ax.plot((sim20['r/R_[-]']-0.5)*2 , sim20['B1Cl_[-]'].values, 'k:', label='OLAF')
ax.plot((sim40['r/R_[-]']-0.5)*2 , sim40['B1Cl_[-]'].values, 'k:')
# ax.plot((sim80['r/R_[-]']-0.5)*2 , sim80['B1Cl_[-]'].values, 'k:')
ax.set_xlabel('y/b [-]')
ax.set_ylabel(r'$C_l$  [-]')
ax.set_ylim([0.47,0.48])
# ax.set_xlim([-1,1])
ax.legend()
ax.tick_params(direction='in')
plt.show()

