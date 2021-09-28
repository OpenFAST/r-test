import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# Local 
import weio


def vel_bump(time, A=1, half=False):
    """ 
    velocity bump, position goes from 0 to A between time[0] and time[-1]
      half is false: velocity 0 -> max -> 0
      half is True:  velocity 0 -> max 

    """
    time-=time[0]
    T = np.max(time)
    if half:
        # instead of going from t=0 to 1, we gofrom t=0 to 0.5
        A = 2*A
        T = T*2
    t = time/T
    x =          A * t**3 * (6*t**2 - 15*t + 10 )
    v = 1/T    * A * 30*t**2 *(1-t)**2
    a = 1/T**2 * A * 60*t *(2*t**2-3*t+1)
    return x, v, a


def sine(time, A=1):
    time-=time[0]
    T = np.max(time)
    omega = 2*np.pi/T
    t= time/T
    x =                    A*np.sin(omega*t)
    v =1/T    *   omega   *A*np.cos(omega*t)
    a =1/T**2 *  -omega**2*A*np.sin(omega*t)
    return x, v, a



# --- Rot Motion
tMax = 10
dt   = 0.1



T  = 2
time  = np.arange(0,tMax+dt/2,dt)

Yaw   = np.zeros((len(time), 3)) # angle, velocity, acc
Pitch = np.zeros((len(time), 3)) # angle, velocity, acc
Rot   = np.zeros((len(time), 3)) # angle, velocity, acc



# --- First period is one rotation of yaw
I = time <= T
Ip= time > T
x,v,a = vel_bump(time[I], 2*np.pi)
Yaw[I,0]+=x
Yaw[I,1]=v
Yaw[I,2]=a
Yaw[Ip,0]+=Yaw[I,0][-1]

# --- Second period we pitch one rotation
I = np.logical_and(time >= T, time<=2*T)
Ip = time>2*T
x,v,a = vel_bump(time[I], 2*np.pi)
Pitch[I,0]+=x
Pitch[I,1]=v
Pitch[I,2]=a
Pitch[Ip,0]+=Pitch[I,0][-1]

# --- Third period we start rotating
I = np.logical_and(time >= 2*T, time<=3*T)
x,v,a = vel_bump(time[I], np.pi/4, half=True)
Rot[I,0]=x
Rot[I,1]=v
Rot[I,2]=a

# --- Constant RPM for the remaining
I=time>3*T
Rot[I,1]=v[-1]
Rot[I,0]=x[-1]+np.cumsum(dt*Rot[I,1])

# --- Fourth period we yaw with some sine motion
I = np.logical_and(time >= 3*T, time<=4*T)

x,v,a = sine(time[I], np.pi/4)
Yaw[I,0]+=x
Yaw[I,1]=v
Yaw[I,2]=a

# --- Fifth period we pitch with some sine motion
I = np.logical_and(time >= 4*T, time<=5*T)

x,v,a = sine(time[I], np.pi/6)
Pitch[I,0]+=x
Pitch[I,1]=v
Pitch[I,2]=a


# --- 
data    = np.column_stack((time, Rot))
df = pd.DataFrame( data=data, columns=['time_[s]', 'azimuth_[rad]','omega_[rad/s]','rotacc_[rad/s^2]']) 
df.to_csv('RotMotion.csv', index=False, sep=',', float_format='%10.6f')

data    = np.column_stack((time, Yaw))
df = pd.DataFrame( data=data, columns=['time_[s]', 'yaw_[rad]','yaw_rate_[rad/s]','yaw_acc_[rad/s^2]']) 
df.to_csv('YawMotion.csv', index=False, sep=',', float_format='%10.6f')

data    = np.column_stack((time, Pitch))
df = pd.DataFrame( data=data, columns=['time_[s]', 'pitch_[rad]','pitch_rate_[rad/s]','pitch_acc_[rad/s^2]']) 
df.to_csv('PitchMotion.csv', index=False, sep=',', float_format='%10.6f')




# fig,ax = plt.subplots(1, 1, sharey=False, figsize=(6.4,4.8)) # (6.4,4.8)
# fig.subplots_adjust(left=0.12, right=0.95, top=0.95, bottom=0.11, hspace=0.20, wspace=0.20)
# ax.plot(time, data[:,1]    , label='x')
# ax.plot(time, data[:,2]    , label='v')
# ax.plot(time, np.concatenate(([0],np.diff(data[:,1])/dt)),'--', label='v2')
# ax.plot(time, data[:,3]    , label='a')
# ax.plot(time, np.concatenate(([0],np.diff(data[:,2])/dt)),'--', label='a2')
# ax.set_xlabel('')
# ax.set_ylabel('')
# ax.legend()
# plt.show()
# # 
