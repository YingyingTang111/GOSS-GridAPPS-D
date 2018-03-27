## Read from simulation results and plot

import numpy as np
import csv
import math
import subprocess, os, shutil #os is used to append the path
import matplotlib.pyplot as plt

# Define path of the files to be read
outputPath = "/home/yingying/git/volttron/TransactiveEnergy-ThreeAgg/GLDtest/Output/"
logPath = "/home/yingying/git/volttron/"
coordinatorPath = "/home/yingying/git/volttron/TransactiveEnergy-ThreeAgg/CoordinatorAgent/coordinator/"
  
# Read substation output from GLD recorder
lines = list(open(outputPath + "total_feeder_load_Meter_1.csv"))
subs = [float(i.split(',+')[1])/1000000.0 for i in lines[9:]]
lines = list(open(outputPath + "PV_1.csv"))
pv = [float(i.split(',')[1]) for i in lines[9:]]
# subs = [(a - b)/1000000.0 for a, b in zip(subs, pv)]
subs = np.array(subs) # unit convert from W to MW
subs = np.mean(subs.reshape(-1, 10), axis=1)
# plt.plot(subs,  color="blue", label="simulated")
# plt.ylabel('feeder substation real power (MW)')

# Read cleared information from Coordinator1_cleared_information.csv
lines = list(open(coordinatorPath + "Coordinator1_cleared_information.csv"))
cleared_p1 = [float(i.split(',')[3]) for i in lines[1:]]
cleared_p2 = [float(i.split(',')[4]) for i in lines[1:]]
cleared_q1 = [float(i.split(',')[5])/1000.0 for i in lines[1:]]
cleared_q2 = [float(i.split(',')[6])/1000.0 for i in lines[1:]]
cleared_DG1 = [float(i.split(',')[7])/1000.0 for i in lines[1:]]
cleared_DG2 = [float(i.split(',')[8])/1000.0 for i in lines[1:]]
cleared_DG3 = [float(i.split(',')[9])/1000.0 for i in lines[1:]]
cleared_DG4 = [float(i.split(',')[10])/1000.0 for i in lines[1:]]
cleared_DG5 = [float(i.split(',')[11])/1000.0 for i in lines[1:]]
plannedSubs = [float(i.split(',')[13])/1000.0 for i in lines[1:]]
expectedSubs = [float(i.split(',')[14])/1000.0 for i in lines[1:]]
totUncontrollable = [float(i.split(',')[15])/1000.0 for i in lines[1:]]


# Plot simulated and expected substation ral power together
plt.figure(1)
plt.plot(subs,  color="blue", label="simulated")
plt.ylabel('feeder substation real power (MW)')
plt.plot(expectedSubs,  color="red", label="expected")
plt.grid(True)

# Plot DG output together
plt.figure(2)
plt.plot(cleared_DG1,  color="r")
plt.plot(cleared_DG2,  color="b")
plt.plot(cleared_DG3,  color="g")
plt.plot(cleared_DG4,  color="k")
plt.plot(cleared_DG5,  color="grey")
plt.ylabel('DG real output (MW)')
plt.grid(True)

# Plot cleared quantity
plt.figure(3)
plt.plot(cleared_p1,  color="r")
plt.plot(cleared_p2,  color="b")
plt.ylabel('cleared controllable load quantity (MW)')
plt.grid(True)

# Plot cleared price
plt.figure(4)
plt.plot(cleared_q1,  color="r")
plt.plot(cleared_q2,  color="b")
plt.ylabel('cleared controllable load price ($)')
plt.grid(True)


# plt.figure(5)
# # plt.plot(subs,  color="blue", label="simulated")
# plt.ylabel('feeder substation real power (MW)')
# plt.plot(subs - expectedSubs,  color="red", label="expected")
# plt.grid(True)






plt.show()




# lines = list(open(outputPath + "PV_1.csv"))
# pv = [float(i.split(',')[1]) for i in lines[9:]]
# subs = [(a - b)/1000000.0 for a, b in zip(subs, pv)]
# subs = np.array(subs) # unit convert from W to MW
# subs = np.mean(subs.reshape(-1, 10), axis=1)
# plt.plot(subs,  color="blue", label="simulated")
# plt.ylabel('feeder substation real power (MW)')




















