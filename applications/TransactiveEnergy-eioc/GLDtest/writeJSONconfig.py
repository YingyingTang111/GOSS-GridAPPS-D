import json
import re
import os
import shutil
import numpy as np

print("Start writing GLD JSON format config file based on fncs_configure.cfg")

filename = 'fncs_configure.txt'
ip = open (filename, "r")

# Loop through the file fncs_configure.cfg
readObj = ''
propList = []
JSONconfig = {}
for line in ip:
    line = line.replace(':', '.')
    line = line.replace('<-', '->')
    lst = line.split('.')
    objTemp = lst[1].replace(" ", "")
    propTemp = lst[2].split('-')[0].replace(" ", "")
    if ((readObj != objTemp) or (propTemp not in propList)):
        if (readObj != objTemp and len(propList) > 0):
            JSONconfig[readObj] = propList # Before processing data of the new object, store properties of the old object
            propList = [] # Empty property list of the new object
        readObj = objTemp
        propList.append(propTemp)
        
# Finish writing the last object properties
if (len(propList) > 0):
    JSONconfig[readObj] = propList # Before processing data of the new object, store properties of the old object
          
# Write the controller information into one config file:
filename = "fncs_configure.json"
GLD_JSONconfig = open(filename, "w")
json.dump(JSONconfig, GLD_JSONconfig)
GLD_JSONconfig.close()
 
ip.close()

print("Finish writing GLD JSON format config file based on fncs_configure.cfg")

