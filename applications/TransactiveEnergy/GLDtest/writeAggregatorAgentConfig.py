import json
import re
import os
import shutil
import numpy as np

print("Start writing aggregator config based on fncs_configure.cfg")

filename = 'fncs_configure.txt'
folderName = "../AggregatorAgent/config"
ip = open (filename, "r")
if not os.path.exists(folderName):
    os.makedirs(folderName)
else:
    shutil.rmtree(folderName) # delete the existing input folder in case there are data not needed
    os.makedirs(folderName)

## parameters to be written into config files
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
bid_delay = 15 # 10
use_predictive_bidding = 0
use_override = "OFF"

# market data:
marketName = "Aggregator_1"
unit = "kW"
periodMarket = periodController
initial_price = 65
fixed_price = 65
std_dev = 16
price_cap = 1000
special_mode = "MD_BUYERS" #"MD_BUYERS"
use_future_mean_price = 0
clearing_scalar = 0.0
latency = 0
ignore_pricecap = 0
ignore_failedmarket = 0
statistic_mode = 1
stat_mode =  ["ST_CURR", "ST_CURR"]
interval = [86400, 86400]
stat_type = ["SY_MEAN", "SY_STDEV"]
aggregator_1 = [22, 24, 28, 29, 30, 31, 32, 33] # Nodes that are part of aggregator 1
aggregator_lines = ['18_21']; # Line name of aggregation point
capacity_reference_object = aggregator_lines[0]
max_capacity_reference_bid_quantity = 5000

# coordinator data:
coordinatorName = 'Coordinator1'

# Loop through the file fncs_configure.cfg
config = {}
config['agentid'] = marketName
# Write subscription
subscriptions = {}
subscriptions['controller'] = []
subscriptions['meter'] = []
subscriptions['fncs_bridge'] = []
subscriptions['coordinator'] = []
controllers = {}
controller= ''
for line in ip:
    # Write subscription
    # controllers data subscribed 
    if ('<-' in line and 'house' in line):
        lst = line.split('<- ')
        controllerName = lst[1].split('/')[1]
        meterName = controllerName.split('_')[-2]
        if (int(meterName) in aggregator_1 and controller != controllerName):
            controller = controllerName            
            controllers[controller] = {}
            controllers[controller]['price'] = {'propertyType': 'double', 'propertyUnit': 'none', 'propertyValue': 0.0}
            controllers[controller]['quantity'] = {'propertyType': 'double', 'propertyUnit': 'none', 'propertyValue': 0.0}
            controllers[controller]['bid_id'] = {'propertyType': 'string', 'propertyUnit': 'none', 'propertyValue': 0}
            controllers[controller]['state'] = {'propertyType': 'string', 'propertyUnit': 'none', 'propertyValue': 'ON'}
            controllers[controller]['rebid'] = {'propertyType': 'integer', 'propertyUnit': 'none', 'propertyValue': 0}
            controllers[controller]['market_id'] = {'propertyType': 'integer', 'propertyUnit': 'none', 'propertyValue': 0}
            
    # Meter data (real power from switch) subscribed  
    meters = {}      
    if ((marketName in line) and (aggregator_lines[0] in line) and ('VAR' not in line)):
        lst = line.split('-> ')
        temp = lst[1].split(';')
        meter = temp[0]
        meters[meter] = {'propertyType': 'double', 'propertyUnit': 'none', 'propertyValue': 0}
        subscriptions['meter'].append(meters)      
        
subscriptions['controller'].append(controllers)

# Write subscription to fncs_bridge message
fncs_bridge = {}
fncs_bridge[fncs_zpl['name']] = {'propertyType': 'String', 'propertyUnit': 'none', 'propertyValue': 0}
subscriptions['fncs_bridge'].append(fncs_bridge)

# data subscribed to aggregator
coordinator = {}
coordinator['market_id'] = {'type': 'integer', 'units': 'none', 'default': 1}
coordinator['fixed_price'] = {'type': 'double', 'units': 'none', 'default': 0.0}
subscriptions['coordinator'].append({coordinatorName:coordinator})
            
# Write initial valuess
initialVal = {}
initialVal = {}
initialVal['market_information'] = {'market_id': 0, 'bid_delay': bid_delay, 'unit': unit, 'special_mode': special_mode, 'use_future_mean_price': use_future_mean_price, 'pricecap': price_cap, 'clearing_scalar': clearing_scalar, \
                                              'period': periodMarket, 'latency': latency, 'fixed_price': fixed_price, 'init_price': initial_price, 'init_stdev': std_dev, 'ignore_pricecap': ignore_pricecap, 'ignore_failedmarket': ignore_failedmarket, \
                                              'statistic_mode': statistic_mode, 'capacity_reference_object': capacity_reference_object, 'max_capacity_reference_bid_quantity': max_capacity_reference_bid_quantity}
initialVal['statistics_information'] = {'stat_mode': stat_mode, 'interval': interval, 'stat_type': stat_type, 'value': [0 for i in range(len(stat_mode))]}
# obtain controller information for market:
controllers_names = []
for key, value in controllers.items(): # Add all controllers
    controllers_names.append(key)
initialVal['controller_information'] = {'name': controllers_names, 'price': [0 for i in range(len(controllers))], 'quantity': [0.0 for i in range(len(controllers))], 'state': ["ON" for i in range(len(controllers))]}

# Finalize config dictionary
config['subscriptions'] = subscriptions
config['initial_value'] = initialVal
        
# Write the controller information into one config file:
filename = folderName + "/" + marketName + "_config.cfg"
op_aggregator = open(filename, "w")
json.dump(config, op_aggregator)
op_aggregator.close()
 
ip.close()

print("Finish writing aggregator config files based on fncs_configure.cfg")

