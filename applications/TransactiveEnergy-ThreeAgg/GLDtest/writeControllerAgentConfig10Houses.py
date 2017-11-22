import json
import re
import os
import shutil
import numpy as np

def write_FNCS_VOLTTRON_Bridge_Config(id, houses):
    
    print("Start writing FNCS_VOLTTRON_Bridge%d.config based on fncs_configure.cfg" % (id))
    
    # Start writing config file
    config = {}
    fncs_zpl = {}
    values = {}
    remote_platform_params = {}
    config['simulation_run_time'] = '24h'
    config['heartbeat_period'] = 1
    config['heartbeat_multiplier'] = 1 # 60
    # Start defining fncs_zpl based on glm config file
    fncs_zpl['name'] = 'FNCS_Volttron_Bridge' + str(id)
    fncs_zpl['time_delta'] = '1s' # 60s
    fncs_zpl['broker'] = 'tcp://localhost:5570'
    
    # Obtain the house names this FNCS_Volttron_Bridge will work with
    
    values = {}
    propertyList = ['air_temperature', 'power_state', 'hvac_load']
    index = 1
    for house in houses:
        houseNames = house.keys()
        if (len(houseNames) != 1):
            raise ValueError('The house key is more than 1')
        else:
            houseName = houseNames[0]
        for property in propertyList:
            topic = houseName + '/' + property
            dict = {}
            dict['topic'] = 'fncs_Test/' + topic
            dict['default'] = '0'
            dict['type'] = 'double'
            dict['list'] = 'fasle'
            values[str(index)] = dict
            index += 1
      
    fncs_zpl['values'] = values
    config['fncs_zpl'] = fncs_zpl
    
    # write remote_platform_params
    remote_platform_params['vip_address'] = 'tcp://127.0.0.1'
    remote_platform_params['port'] = 22916
    remote_platform_params['agent_public'] = 'cDc4_Lli13dt-__ju-vpgAeOEbbRPaOVzQoeQ5KHjUk'
    remote_platform_params['agent_secret'] = 'k19_VwSSfbFUzm4Op3DGBlOH6Vd7rMJWy4iQo_t-wuw'
    remote_platform_params['server_key'] = 'XDMM3_KrXqSaaPXEM3vL7rumk4nd-A30dcksjfFWNyM'
    config['remote_platform_params'] = remote_platform_params
    
    # Write the dictionary into JSON file
    filenameFNCS = '../FncsVolttronBridge/FNCS_VOLTTRON_Bridge' + str(id) + '.config'
    with open(filenameFNCS, 'w') as outfile:
        json.dump(config, outfile)
    
    print("Finish writing FNCS_VOLTTRON_Bridge%d.config based on fncs_configure.cfg" % (id))
           
    return


print("Start writing config based on fncs_configure.cfg")

filename_conf = 'fncs_configure.txt'
folderName = "../ControllerAgent/config"
ip = open (filename_conf, "r")
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
countHouse = 1
groupController = 1
groupNum = 10 # adjustable
aggregatorNamePrev = 'default'
isNewAgg = False

# Creat a dictionary storing house name
allHouseDict = {}
#
for line in ip:
    if ('->' in line and ('house' in line)):
        lst = line.split('-> ')
        houseName = lst[0].split('.')[0]
        houseName = houseName[houseName.find('house'):]
        if (controlledHouse != houseName):
            # Find aggregator name
            meterName = houseName.split('_')[-2]
            if (int(meterName) in aggregator_1):
                aggregatorName = aggregator_Names[0]
            elif (int(meterName) in aggregator_2):
                aggregatorName = aggregator_Names[1]
            elif (int(meterName) in aggregator_3):
                aggregatorName = aggregator_Names[2]
            
            if (aggregatorNamePrev != 'default' and aggregatorNamePrev != aggregatorName):
                isNewAgg = True
                print('At group %d, new type of aggregator encountered', groupController)
                 
            elif (aggregatorNamePrev == 'default'):
                aggregatorNamePrev = aggregatorName 
 
            # 
            if isNewAgg == False:
                              
                if (countHouse == 1):
                    config10 = {}
                    config10['agentid'] = 'controller' + str(groupController)
                    config10['houses'] = []
                config = {}
                HouseDict = {houseName: None}
        #             config10[houseName] = {}
                controlledHouse = houseName
                controllerName = 'controller_' + houseName
        #             config['agentid'] = controllerName
            
            
                # Write subscription
                subscriptions = {}
                subscriptions['house'] = []
#                 subscriptions['aggregator'] = []
    #             subscriptions['fncs_bridge'] = []
    
                # data subscribed to house
                house = {}
                house['air_temperature'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                house['power_state'] = {'type': 'string', 'units': 'none', 'default': 'ON'}
                house['hvac_load'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                subscriptions['house'].append({controlledHouse: house})
                
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
#                 initialVal['aggregator_information'] = {'market_id': 0, 'aggregator_unit': unit, 'initial_price': initial_price, 'average_price': initial_price, 'std_dev': std_dev, 'clear_price': initial_price, 'price_cap': price_cap, 'period': periodAggregator}
    
                # Finalize config dictionary
                config['subscriptions'] = subscriptions
                config['initial_value'] = initialVal
            
                # Store the config of this house into config10:
                HouseDict[houseName] = config
                config10['houses'].append(HouseDict)
                
                # Write subscription to fncs_bridge message
                config10['fncs_bridge'] = []
                fncs_bridge = {}
                fncs_bridge[fncs_zpl['name']] = {'propertyType': 'String', 'propertyUnit': 'none', 'propertyValue': 0}
                config10['fncs_bridge'].append(fncs_bridge)
                
                # Aggregator information initialization
                config10['aggregator_information'] = {'market_id': 0, 'aggregator_unit': unit, 'initial_price': initial_price, 'average_price': initial_price, 'std_dev': std_dev, 'clear_price': initial_price, 'price_cap': price_cap, 'period': periodAggregator}

                # data subscribed to aggregator
                config10['aggregator'] = []
                aggregator = {}
                aggregator['market_id'] = {'type': 'integer', 'units': 'none', 'default': 1}
                aggregator['initial_price'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                aggregator['average_price'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                aggregator['std_dev'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                aggregator['clear_price'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                aggregator['price_cap'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                config10['aggregator'].append({aggregatorName:aggregator})
                
                
                # Write the controller config10 information into one config file when reaching the group numbers defined:
                if (countHouse == groupNum):
                    
                    # Store all houses in the same group
                    allHouseDict[groupController] = []
                    houses = config10['houses']
                    for house in houses:
                        name_temp = house.keys()
                        if (len(name_temp) != 1):
                            raise ValueError('The house key is more than 1')
                        else:
                            name_temp = name_temp[0]
                            allHouseDict[groupController].append(name_temp)
                    
                    # Write FNCS_VOLTTRON_Bridge configureation file
                    write_FNCS_VOLTTRON_Bridge_Config(groupController, config10['houses'])
                    
                    #
                    filename = folderName + "/controller_" + str(groupController) + "_config.cfg"
                    op_controller = open(filename, "w")
                    json.dump(config10, op_controller)
                    op_controller.close()
                    groupController += 1
                    countHouse = 1
                else:
                    countHouse += 1
            
            else:
                # Write the previous house information into the cfg file, without including current house information
                # Write subscription to fncs_bridge message
                config10['fncs_bridge'] = []
                fncs_bridge = {}
                fncs_bridge[fncs_zpl['name']] = {'propertyType': 'String', 'propertyUnit': 'none', 'propertyValue': 0}
                config10['fncs_bridge'].append(fncs_bridge)
                
                # Aggregator information initialization
                config10['aggregator_information'] = {'market_id': 0, 'aggregator_unit': unit, 'initial_price': initial_price, 'average_price': initial_price, 'std_dev': std_dev, 'clear_price': initial_price, 'price_cap': price_cap, 'period': periodAggregator}

                # data subscribed to aggregator
                config10['aggregator'] = []
                aggregator = {}
                aggregator['market_id'] = {'type': 'integer', 'units': 'none', 'default': 1}
                aggregator['initial_price'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                aggregator['average_price'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                aggregator['std_dev'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                aggregator['clear_price'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                aggregator['price_cap'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                config10['aggregator'].append({aggregatorNamePrev:aggregator})
                aggregatorNamePrev = aggregatorName
                
                # Write FNCS_VOLTTRON_Bridge configureation file
                write_FNCS_VOLTTRON_Bridge_Config(groupController, config10['houses'])
                
                # Store all houses in the same group
                allHouseDict[groupController] = []
                houses = config10['houses']
                for house in houses:
                    name_temp = house.keys()
                    if (len(name_temp) != 1):
                        raise ValueError('The house key is more than 1')
                    else:
                        name_temp = name_temp[0]
                        allHouseDict[groupController].append(name_temp)
                
                # Write the controller config10 information into one config file when reaching the group numbers defined:
                filename = folderName + "/controller_" + str(groupController) + "_config.cfg"
                op_controller = open(filename, "w")
                json.dump(config10, op_controller)
                op_controller.close()
                groupController += 1
                countHouse = 1
                
                # Store current house infomation
                config10 = {}
                config10['agentid'] = 'controller' + str(groupController)
                config10['houses'] = []
                config = {}
                HouseDict = {houseName: None}
        #             config10[houseName] = {}
                controlledHouse = houseName
                controllerName = 'controller_' + houseName
        #             config['agentid'] = controllerName

                # Write subscription
                subscriptions = {}
                subscriptions['house'] = []
#                 subscriptions['aggregator'] = []
    #             subscriptions['fncs_bridge'] = []
    
                # data subscribed to house
                house = {}
                house['air_temperature'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                house['power_state'] = {'type': 'string', 'units': 'none', 'default': 'ON'}
                house['hvac_load'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                subscriptions['house'].append({controlledHouse: house})
                
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
#                 initialVal['aggregator_information'] = {'market_id': 0, 'aggregator_unit': unit, 'initial_price': initial_price, 'average_price': initial_price, 'std_dev': std_dev, 'clear_price': initial_price, 'price_cap': price_cap, 'period': periodAggregator}
    
                # Finalize config dictionary
                config['subscriptions'] = subscriptions
                config['initial_value'] = initialVal
            
                # Store the config of this house into config10:
                HouseDict[houseName] = config
                config10['houses'].append(HouseDict)
                
                isNewAgg = False
                countHouse += 1

 
ip.close()

print("Finish writing controller config files based on fncs_configure.cfg")

# Need to rearrange GLD config file
ip = open (filename_conf, "r")
op = open ('fncs_configure_cd.txt', "w")
for line in ip:
    if ('house' in line and 'FNCS_Volttron_Bridge' in line):
        temp = line.split(':')
        houseName = temp[1].split('.')[0]
        for key, val in allHouseDict.items():
            if houseName in val:
                break
        replaceName = 'FNCS_Volttron_Bridge' + str(key)
        line = line.replace('FNCS_Volttron_Bridge', replaceName)
    op.write(line)
    
ip.close()
op.close()

# Write bash file to run all FNCS_VOLTTRON_BRIDGE.py agents together
folderName = "../FncsVolttronBridge"
filename = folderName + '/runFNCS_VOLTTRON_BRIDGE.sh'
op = open (filename, "w")
numBridge = len(allHouseDict)
for i in range(numBridge):
    input = 'python FNCS_Volttron_Bridge.py ' + 'fncs/input' + str(i+1) + ' FNCS_VOLTTRON_Bridge' + str(i+1) + '.config ' + str(i+1) + ' &> FNCS_VOLTTRON_Bridge' + str(i+1) + '.log & \n'
    op.write(input)
op.close()







