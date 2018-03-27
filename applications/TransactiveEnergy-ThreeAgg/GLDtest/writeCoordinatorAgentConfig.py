import json
import re
import os
import shutil
import numpy as np

print("Start writing coordinator config based on aggregator configuration files")

inputFolderName = "../AggregatorAgent/config"
outputFolderName = "../CoordinatorAgent/config"
if not os.path.exists(outputFolderName):
    os.makedirs(outputFolderName)
else:
    shutil.rmtree(outputFolderName) # delete the existing input folder in case there are data not needed
    os.makedirs(outputFolderName)

# parameters to be written into config files
# Subscription to FNCS_Bridge simulation_end message
fncs_zpl = {}
fncs_zpl['name'] = 'FNCS_Volttron_Bridge'
fncs_zpl['fncs_bridge_termination_topic'] = fncs_zpl['name']+'/simulation_end'

#
agentName = "Coordinator1"

# market data:
market_id = 1 # Coordinator starts with market id of 1, instead of 0 as in aggregator and controller
bid_delay = 0.0
unit = "kW"
periodCoordinator = 60 * 5
price_cap = 1000
total_feeder_load = 'total_feeder_load.csv' # The file storing total feeder loads without controllers and DGs
bidmode = 'double_price_ver2' # or 'normal' version # double_price_ver2

# Aggregator data:
AggregatorName = []
for file in os.listdir(inputFolderName):
    if file.endswith("_config.cfg"):
        fileName = file[:-11]
        AggregatorName.append(fileName)

# Distributed generation data:
# numDG = 2
# a1 = 0.25
# b1 = 15.6
# c1 = 330
# a2 = 0.31
# b2 = 29.7
# c2 = 300
# rangeL1 = 0.03
# rangeL2 = 0.02
# rangeH1 = 0.3
# rangeH2 = 0.25
# DGpara = [[a1, b1, c1], [a2, b2, c2]]
# DGrange = [[rangeL1, rangeH1], [rangeL2, rangeH2]]

# Loop through the file fncs_configure.cfg
config = {}
config['agentid'] = agentName

# Write subscription
subscriptions = {}
subscriptions['aggregators'] = []
aggregators = {}
for aggregator in AggregatorName:
    # Write subscription
    # Aggregators data subscribed          
    aggregators[aggregator] = {}
    aggregators[aggregator]['price'] = {'propertyType': 'array', 'propertyUnit': 'none', 'propertyValue': ''}
    aggregators[aggregator]['quantity'] = {'propertyType': 'array', 'propertyUnit': 'none', 'propertyValue': ''}
    aggregators[aggregator]['name'] = {'propertyType': 'array', 'propertyUnit': 'none', 'propertyValue': ''}
    aggregators[aggregator]['Q_min'] = {'propertyType': 'array', 'propertyUnit': 'none', 'propertyValue': ''}
    aggregators[aggregator]['Q_max'] = {'propertyType': 'array', 'propertyUnit': 'none', 'propertyValue': ''}
subscriptions['aggregators'].append(aggregators)
# Read in fncs_configure.txt file to obtain the aggregator kVAR load publication information
filename = 'fncs_configure.txt'
ip = open (filename, "r")
# metered loads
subscriptions['aggregator_kW'] = []
subscriptions['aggregator_kVAR'] = []
aggregators_kW = {}
aggregators_kVAR = {}
for aggregator in AggregatorName:
    aggregators_kW[aggregator] = {}
    aggregators_kVAR[aggregator] = {}
    ip.seek(0, 0)
    # Meter data (reactive power from aggregator) subscribed  
    for line in ip:      
        if (aggregator in line and 'VAR' in line):
            line = line.replace('->', '.')
            meterName = line.replace(':', '.').split('.')[1]
            prop = line.split('.')[1].replace(" ", "")
            aggregators_kVAR[aggregator][meterName] = {}
            aggregators_kVAR[aggregator][meterName][prop] = {'propertyType': 'double', 'propertyUnit': 'none', 'propertyValue': 0}
        elif (aggregator in line):
            line = line.replace('->', '.')
            meterName = line.replace(':', '.').split('.')[1]
            prop = line.split('.')[1].replace(" ", "")
            aggregators_kW[aggregator][meterName] = {}
            aggregators_kW[aggregator][meterName][prop] = {'propertyType': 'double', 'propertyUnit': 'none', 'propertyValue': 0}
            
subscriptions['aggregator_kW'].append(aggregators_kW)           
subscriptions['aggregator_kVAR'].append(aggregators_kVAR)

# Meter data (real power from aggregated loads, and individual DG) subscribed   
# meterLoads = ['Meter_18_135', 'Meter_57_60']
meterDGs = ['DG_57', 'DG_152', 'DG_7', 'DG_18', 'DG_56']
# Read in fncs_configure.txt file to obtain the metered load publication information
# metered loads
subscriptions['metered_loads'] = []
meters = {}
# for meter in meterLoads:
#     meters[meter] = {}
#     ip.seek(0, 0)
#     # Meter data (real power from switch) subscribed  
#     for line in ip:      
#         if (meter in line):
#             lst = line.split('-> ')
#             temp = lst[1].split(';')
#             meters[meter][temp[0]] = {'propertyType': 'double', 'propertyUnit': 'none', 'propertyValue': 0}
# #             break
# metered substation load
meter = 'substation_load'
meterkVAR = 'substation_kVAR_load'
meters['Meter_substation'] = {}
ip.seek(0, 0)
for line in ip:      
        if (meter in line or meterkVAR in line):
            line = line.replace('->', '.')
            meterName = line.replace(':', '.').split('.')[1]
            temp = line.split('.')[1].replace(" ", "")
            if (meterName not in meters['Meter_substation'].keys()):
                meters['Meter_substation'][meterName] = {}
            meters['Meter_substation'][meterName][temp] = {'propertyType': 'double', 'propertyUnit': 'none', 'propertyValue': 0}

#             break    


subscriptions['metered_loads'].append(meters)

# generators
meters = {}
subscriptions['metered_DGs'] = []
powers = ['power_A', 'power_B', 'power_C']
for meter in meterDGs:
    meters[meter] = {}
    ip.seek(0, 0)
    # Meter data (real power from switch) subscribed  
    for line in ip:  
        if (meter in line and '->' in line):  
            line = line.replace('->', '.')
            temp = line.split('.')[1].replace(" ", "")
            meters[meter][temp] = {'propertyType': 'double', 'propertyUnit': 'none', 'propertyValue': 0}

subscriptions['metered_DGs'].append(meters)

# Write subscription to fncs_bridge message
subscriptions['fncs_bridge'] = []
fncs_bridge = {}
fncs_bridge[fncs_zpl['name']] = {'propertyType': 'String', 'propertyUnit': 'none', 'propertyValue': 0}
subscriptions['fncs_bridge'].append(fncs_bridge)
   
# Write initial valuess
initialVal = {}
initialVal = {}
initialVal['market_information'] = {'market_id': 0, 'bid_delay': bid_delay, 'unit': unit, 'period': periodCoordinator, 'pricecap': price_cap, 'total_feeder_load': total_feeder_load, 'bidmode': bidmode}
bus = {}
bus['bus_18'] = ['Aggregator_1', 'Aggregator_2']
bus['bus_57'] = ['Aggregator_3']
initialVal['aggregator_information'] = bus
DERinfo = {'DG_152': 1, 'DG_57': 3, 'DG_7': 0, 'DG_18': 2, 'DG_56': 4}
initialVal['DER_information'] = DERinfo

# Finalize config dictionary
config['subscriptions'] = subscriptions
config['initial_value'] = initialVal
        
# Write the controller information into one config file:
filename = outputFolderName + "/" + agentName + "_config.cfg"
op_coordinator = open(filename, "w")
json.dump(config, op_coordinator)
op_coordinator.close()

print("Finish writing coordinator config files based on fncs_configure.cfg")

