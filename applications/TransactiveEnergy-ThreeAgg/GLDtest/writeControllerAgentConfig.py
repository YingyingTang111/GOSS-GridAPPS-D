import json
import re
import os
import shutil
import numpy as np

print("Start writing config based on fncs_configure.cfg")

filename = 'fncs_configure.txt'
folderName = "../ControllerAgent/config"
ip = open (filename, "r")
if not os.path.exists(folderName):
    os.makedirs(folderName)
else:
    shutil.rmtree(folderName) # delete the existing input folder in case there are data not needed
    os.makedirs(folderName)

# parameters to be written into config files
# Subscription to FNCS_Bridge simulation_end message
fncs_zpl = {}
fncs_zpl['name'] = 'FNCS_Volttron_Bridge'
fncs_zpl['fncs_bridge_termination_topic'] = fncs_zpl['name']+'/simulation_end'
# controller data:
periodController = 60 * 5
control_mode = "CN_RAMP"
min_ramp_high = 1.5
max_ramp_high = 2.5
min_range_high = 1.5
max_range_high = 2.5
# used with np.random.uniform below
min_ramp_low = 1.5
max_ramp_low = 2.5
min_range_low = -3.0
max_range_low = -2.0
min_base_setpoint = 76.0
max_base_setpoint = 80.0
bid_delay = 30 # 15
use_predictive_bidding = 0
use_override = "OFF"

# market data:
aggregator_1 = [22, 24, 28, 29, 30, 31, 32, 33] # Nodes that are part of aggregator 1
aggregator_2 = [35, 37, 38, 39, 41, 42, 43, 45, 46, 47, 48, 49, 50, 51] # Nodes that are part of aggregator 2
aggregator_3 = [60, 62, 63, 64, 65, 66, 68, 69, 70, 71, 73, 74, 75, 76, 77, 79, 80, 82, 83, 84, 85, 86, 87, 88, 90, 92, 94, 95, 96, 98, 99, 100, 102, 103, 104, 106, 107, 109, 111, 112, 113, 114] # Nodes that are part of aggregator 3
aggregator_Names = ["Aggregator_1", "Aggregator_2", "Aggregator_3"]

unit = "kW"
periodAggregator = 60
initial_price = 65.00
std_dev = 16.00 # 0.00361
price_cap = 1000

# Loop through the file fncs_configure.cfg
controlledHouse = ''
for line in ip:
    if ('->' in line and ('house' in line)):
        config = {}
        lst = line.split('-> ')
        houseName = lst[0].split('.')[0]
        houseName = houseName[houseName.find('house'):]
        if (controlledHouse != houseName):
            controlledHouse = houseName
            controllerName = 'controller_' + houseName
            config['agentid'] = controllerName
            
            # Find aggregator name
            meterName = houseName.split('_')[-2]
            if (int(meterName) in aggregator_1):
                aggregatorName = aggregator_Names[0]
            elif (int(meterName) in aggregator_2):
                aggregatorName = aggregator_Names[1]
            elif (int(meterName) in aggregator_3):
                aggregatorName = aggregator_Names[2]
            
            # Write subscription
            subscriptions = {}
            subscriptions['house'] = []
            subscriptions['aggregator'] = []
            subscriptions['fncs_bridge'] = []
            # data subscribed to aggregator
            aggregator = {}
            aggregator['market_id'] = {'type': 'integer', 'units': 'none', 'default': 1}
            aggregator['initial_price'] = {'type': 'double', 'units': 'none', 'default': 0.0}
            aggregator['average_price'] = {'type': 'double', 'units': 'none', 'default': 0.0}
            aggregator['std_dev'] = {'type': 'double', 'units': 'none', 'default': 0.0}
            aggregator['clear_price'] = {'type': 'double', 'units': 'none', 'default': 0.0}
            aggregator['price_cap'] = {'type': 'double', 'units': 'none', 'default': 0.0}
            subscriptions['aggregator'].append({aggregatorName:aggregator})
            # data subscribed to house
            house = {}
            house['air_temperature'] = {'type': 'double', 'units': 'none', 'default': 0.0}
            house['power_state'] = {'type': 'string', 'units': 'none', 'default': 'ON'}
            house['hvac_load'] = {'type': 'double', 'units': 'none', 'default': 0.0}
            subscriptions['house'].append({controlledHouse: house})
            # Write subscription to fncs_bridge message
            fncs_bridge = {}
            fncs_bridge[fncs_zpl['name']] = {'propertyType': 'String', 'propertyUnit': 'none', 'propertyValue': 0}
            subscriptions['fncs_bridge'].append(fncs_bridge)
            
            # Write initial valuess
            initialVal = {}
            ramp_low = np.random.uniform (min_ramp_low, max_ramp_low)
            range_low = np.random.uniform (min_range_low, max_range_low)
            ramp_high = np.random.uniform (min_ramp_high, max_ramp_high)
            range_high = np.random.uniform (min_range_high, max_range_high)
            base_setpoint = np.random.uniform (min_base_setpoint, max_base_setpoint)
            initialVal['controller_information'] = {'control_mode': control_mode, 'aggregatorName': aggregatorName, 'houseName': controlledHouse, 'bid_id': controllerName, 'period': periodController, \
                       'ramp_low': ramp_low, 'ramp_high': ramp_high, 'range_low': range_low, 'range_high': range_high, 'base_setpoint': base_setpoint, \
                       'bid_delay': bid_delay, 'use_predictive_bidding': use_predictive_bidding, 'use_override': use_override}
            initialVal['aggregator_information'] = {'market_id': 0, 'aggregator_unit': unit, 'initial_price': initial_price, 'average_price': initial_price, 'std_dev': std_dev, 'clear_price': initial_price, 'price_cap': price_cap, 'period': periodAggregator}

            # Finalize config dictionary
            config['subscriptions'] = subscriptions
            config['initial_value'] = initialVal
            
            # Write the controller information into one config file:
            filename = folderName + "/controller_" + controlledHouse + "_config.cfg"
            op_controller = open(filename, "w")
            json.dump(config, op_controller)
            op_controller.close()
 
ip.close()

print("Finish writing controller config files based on fncs_configure.cfg")

