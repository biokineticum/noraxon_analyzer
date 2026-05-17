import pandas as pd
import numpy as np
import sys

def compute_velocity(accel, time):
    dt = np.diff(time)
    vel = np.zeros(len(accel))
    vel[1:] = np.cumsum( (accel[:-1] + accel[1:]) / 2 * dt )
    return vel

if __name__ == '__main__':
    G_TO_MPS2 = 9.80665
    MILLI_G_TO_MPS2 = G_TO_MPS2 / 1000

    # dummy test
    time = np.linspace(0, 0.6, 1200)
    ax = np.random.normal(0, 1, 1200)
    ay = np.random.normal(9.8, 1, 1200)
    az = np.random.normal(0, 1, 1200)
    
    vx = compute_velocity(ax, time)
    vy = compute_velocity(ay, time)
    vz = compute_velocity(az, time)
    
    vres = np.sqrt(vx**2 + vy**2 + vz**2)
    print("max vy:", np.max(vy))
    print("max vres:", np.max(vres))
