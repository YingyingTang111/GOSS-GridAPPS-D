import json
import csv
import re
import os
import shutil
import numpy as np

print("Start recording Qh and hvac values based on pre-run gld simulation results")

inputQhFolderName = "Output/Qh"
inputHVACFolderName = "Output/hvac"

# parameters to be written into config files
# Subscription to FNCS_Bridge simulation_end message
hvacHouses = {}
QhHouses = {}

# Qh data:
for file in os.listdir(inputQhFolderName):
    data = []
    houseName = ""
    readName = False
    with open(inputQhFolderName + '/' + file) as fobj:
#         print (file)
        for line in fobj:
            row = line.split(',')
            if len(row) > 10:
                if readName == False:
                    houseName = row[1:]
                    readName = True
                else:
                    data.append([float(i) for i in row[1:]])
        dataArray = np.array(data)
        avg = np.true_divide(dataArray.sum(0),(dataArray!=0).sum(0))
        for i in range(len(houseName)):
            name = houseName[i].split(':')[0]
            QhHouses[name] = avg[i]

# hvac data
for file in os.listdir(inputHVACFolderName):
    data = []
    houseName = ""
    readName = False
    with open(inputHVACFolderName + '/' + file) as fobj:
        for line in fobj:
            row = line.split(',')
            if len(row) > 10:
                if readName == False:
                    houseName = row[1:]
                    readName = True
                else:
                    data.append([float(i) for i in row[1:]])
        dataArray = np.array(data)
        avg = np.true_divide(dataArray.sum(0),(dataArray!=0).sum(0))
        for i in range(len(houseName)):
            name = houseName[i].split(':')[0]
            hvacHouses[name] = avg[i]

print('finish recording Qh and hvac values based on pre-run gld simulation results')       
#     with open(inputQhFolderName + '/' + file, 'rb') as f:
#         
#         reader = csv.reader(f)
#         Qh_list = list(reader)
#         Qh_house_name = Qh_list[7][1:]
#         Qh_val = Qh_list[8:]
#         l = np.array(Qh_val)[1:,:]
#         ans= l.sum(1)/(l != 0).sum(1)
#         ans=np.apply_along_axis(lambda v: np.mean(l[np.nonzero(v)]), 0, l)
#         average = l[np.nonzero(l)].mean()
        
        

