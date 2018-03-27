import json
import re
import os
import shutil
import numpy as np

print("Start writing config based on fncs_configure.txt")

##
print("Firstly get setpoint of each house written in IEEE_123_mod.glm")
glm_filename = "IEEE_123_mod.glm"
houseSetpointDict = {}
ip = open (glm_filename, "r")
controlledHouse = ""
inHouse = False
endedHouse = False
for line in ip:
    lst = line.split()
    if len(lst) > 1:
        if lst[1] == "house":
            inHouse = True
        if inHouse == True and lst[0] == "object" and lst[1] != "house":
            endedHouse = True
        if inHouse == True and lst[0] == "name" and endedHouse == False:
            houseName = lst[1].strip(";")
        if inHouse == True and lst[0] == "cooling_setpoint" and endedHouse == False:
            setpoint = float(lst[1].strip(";"))
            houseSetpointDict[houseName] = setpoint
    elif len(lst) == 1:
        if inHouse == True:
            inHouse = False
            endedHouse = False

ip.close()

##
print("Then, write config based on fncs_configure.txt")

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
control_mode = "CN_DOUBLE_PRICE_ver2" #"CN_RAMP" or "CN_DOUBLE_PRICE_ver2" or "CN_DOUBLE_PRICE"
min_ramp_high = 0.5 #1.0 #1.5
max_ramp_high = 15 #3.0 #2.5
min_range_high = 6.0 #1.5
max_range_high = 8.0 #2.5
# used with np.random.uniform below
min_ramp_low = 0.5 #1.0 #1.5
max_ramp_low = 15 #3.0 #2.5
min_range_low = -8.0 #-3.0
max_range_low = -6 # -2.0
min_base_setpoint = 70 #76.0
max_base_setpoint = 74 #80.0
bid_delay = 13 # 15
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
min_ctrl_cap = 900
max_ctrl_cap = 50

# Loop through the file fncs_configure.cfg
controlledHouse = ''
countHouse = 1
groupController = 1
groupNum = 10 # adjustable
aggregatorNamePrev = 'default'
isNewAgg = False

# If controller mode is double_price mode, need to pre-run GLD simulations to record all houses' hvac and Qh values
if (control_mode == "CN_DOUBLE_PRICE" or control_mode == "CN_DOUBLE_PRICE_ver2"):
    print("Start recording Qh and hvac values based on pre-run gld simulation results")

    inputQhFolderName = "Qh"
    inputHVACFolderName = "hvac"
    
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

# Creat a dictionary storing house name
allHouseDict = {}
aggHVAC = 0
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
                print('At group ', groupController, ', new type of aggregator encountered')
                 
            elif (aggregatorNamePrev == 'default'):
                aggregatorNamePrev = aggregatorName 
 
            # 
            if isNewAgg == False:
                              
                if (countHouse == 1):
                    configAgg = {}
                    configAgg['agentid'] = 'controller_' + str(groupController)
                    configAgg['houses'] = []
                config = {}
                HouseDict = {houseName: None}
        #             configAgg[houseName] = {}
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
#                 house['hvac_load'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                house['UA'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                house['mass_heat_coeff'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                house['air_heat_capacity_cd'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                house['mass_heat_capacity'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                house['solar_gain'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                house['Qi'] = {'type': 'double', 'units': 'none', 'default': 0.0}
#                 house['heat_cool_gain'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                house['outdoor_temperature'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                house['mass_temperature'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                house['design_cooling_capacity'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                subscriptions['house'].append({controlledHouse: house})
                
                # Write initial valuess
                initialVal = {}
                ramp_low = np.random.uniform (min_ramp_low, max_ramp_low)
                range_low = np.random.uniform (min_range_low, max_range_low)
                ramp_high = ramp_low # np.random.uniform (min_ramp_high, max_ramp_high)
                range_high = np.random.uniform (min_range_high, max_range_high)
                # Obtain house setpoint from glm file 
                base_setpoint = houseSetpointDict[houseName] #np.random.uniform (min_base_setpoint, max_base_setpoint)
                ctrl_cap = np.random.uniform (min_ctrl_cap, max_ctrl_cap)
                initialVal['controller_information'] = {'control_mode': control_mode, 'aggregatorName': aggregatorName, 'houseName': controlledHouse, 'bid_id': controllerName, 'period': periodController, \
                           'ramp_low': ramp_low, 'ramp_high': ramp_high, 'range_low': range_low, 'range_high': range_high, 'base_setpoint': base_setpoint, \
                           'bid_delay': bid_delay, 'use_predictive_bidding': use_predictive_bidding, 'use_override': use_override, 'ctrl_cap': ctrl_cap, \
                           'hvac_load': hvacHouses[controlledHouse], 'heat_cool_gain': QhHouses[controlledHouse]
                           }
#                 initialVal['aggregator_information'] = {'market_id': 0, 'aggregator_unit': unit, 'initial_price': initial_price, 'average_price': initial_price, 'std_dev': std_dev, 'clear_price': initial_price, 'price_cap': price_cap, 'period': periodAggregator}
    
                # Finalize config dictionary
                config['subscriptions'] = subscriptions
                config['initial_value'] = initialVal
            
                # Store the config of this house into configAgg:
                HouseDict[houseName] = config
                configAgg['houses'].append(HouseDict)
                
                # Write subscription to fncs_bridge message
                configAgg['fncs_bridge'] = []
                fncs_bridge = {}
                fncs_bridge[fncs_zpl['name']] = {'propertyType': 'String', 'propertyUnit': 'none', 'propertyValue': 0}
                configAgg['fncs_bridge'].append(fncs_bridge)
                
                # Aggregator information initialization
                configAgg['aggregator_information'] = {'market_id': 0, 'aggregator_unit': unit, 'initial_price': initial_price, 'average_price': initial_price, 'std_dev': std_dev, 'clear_price': initial_price, 'price_cap': price_cap, 'period': periodAggregator}

                # data subscribed to aggregator
                configAgg['aggregator'] = []
                aggregator = {}
                aggregator['market_id'] = {'type': 'integer', 'units': 'none', 'default': 1}
                aggregator['initial_price'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                aggregator['average_price'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                aggregator['std_dev'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                aggregator['clear_price'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                aggregator['price_cap'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                configAgg['aggregator'].append({aggregatorName:aggregator})
                
                
                # Write the controller configAgg information into one config file when reaching the group numbers defined:
                countHouse += 1
                aggHVAC += hvacHouses[controlledHouse]
                # if (countHouse == groupNum):
                    
                    # # Store all houses in the same group
                    # allHouseDict[groupController] = []
                    # houses = configAgg['houses']
                    # for house in houses:
                        # name_temp = house.keys()
                        # if (len(name_temp) != 1):
                            # raise ValueError('The house key is more than 1')
                        # else:
                            # name_temp = name_temp[0]
                            # allHouseDict[groupController].append(name_temp)
                    
                    # # Write FNCS_VOLTTRON_Bridge configureation file
# #                     write_FNCS_VOLTTRON_Bridge_Config(groupController, configAgg['houses'])
                    
                    # #
                    # filename = folderName + "/controller_" + str(groupController) + "_config.cfg"
                    # op_controller = open(filename, "w")
                    # json.dump(configAgg, op_controller)
                    # op_controller.close()
                    # groupController += 1
                    # countHouse = 1
                # else:
                    # countHouse += 1
            
            else:
                # Write the previous house information into the cfg file, without including current house information
                # Write subscription to fncs_bridge message
                configAgg['fncs_bridge'] = []
                fncs_bridge = {}
                fncs_bridge[fncs_zpl['name']] = {'propertyType': 'String', 'propertyUnit': 'none', 'propertyValue': 0}
                configAgg['fncs_bridge'].append(fncs_bridge)
                
                # Aggregator information initialization
                configAgg['aggregator_information'] = {'market_id': 0, 'aggregator_unit': unit, 'initial_price': initial_price, 'average_price': initial_price, 'std_dev': std_dev, 'clear_price': initial_price, 'price_cap': price_cap, 'period': periodAggregator}

                # data subscribed to aggregator
                configAgg['aggregator'] = []
                aggregator = {}
                aggregator['market_id'] = {'type': 'integer', 'units': 'none', 'default': 1}
                aggregator['initial_price'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                aggregator['average_price'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                aggregator['std_dev'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                aggregator['clear_price'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                aggregator['price_cap'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                configAgg['aggregator'].append({aggregatorNamePrev:aggregator})
                aggregatorNamePrev = aggregatorName
                
                # Write FNCS_VOLTTRON_Bridge configureation file
#                 write_FNCS_VOLTTRON_Bridge_Config(groupController, configAgg['houses'])
                
                # Store all houses in the same group
                allHouseDict[groupController] = []
                houses = configAgg['houses']
                for house in houses:
                    name_temp = house.keys()
                    if (len(name_temp) != 1):
                        raise ValueError('The house key is more than 1')
                    else:
                        name_temp = name_temp[0]
                        allHouseDict[groupController].append(name_temp)
                
                # Write the controller configAgg information into one config file when reaching the group numbers defined:
                print('At aggregated group ', groupController, ', config files of all ', countHouse, ' houses controlled are written, with total hvac: ', aggHVAC)
                filename = folderName + "/controller_" + str(groupController) + "_config.cfg"
                op_controller = open(filename, "w")
                json.dump(configAgg, op_controller)
                op_controller.close()
                groupController += 1
                countHouse = 1
                aggHVAC = 0
                
                # Store current house infomation
                configAgg = {}
                configAgg['agentid'] = 'controller_' + str(groupController)
                configAgg['houses'] = []
                config = {}
                HouseDict = {houseName: None}
        #             configAgg[houseName] = {}
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
                house['UA'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                house['mass_heat_coeff'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                house['air_heat_capacity_cd'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                house['mass_heat_capacity'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                house['solar_gain'] = {'type': 'double', 'units': 'none', 'default': 0.0}
#                 house['heat_cool_gain'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                house['outdoor_temperature'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                house['mass_temperature'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                house['design_cooling_capacity'] = {'type': 'double', 'units': 'none', 'default': 0.0}
                subscriptions['house'].append({controlledHouse: house})
                
                # Write initial valuess
                initialVal = {}
                ramp_low = np.random.uniform (min_ramp_low, max_ramp_low)
                range_low = np.random.uniform (min_range_low, max_range_low)
                ramp_high = np.random.uniform (min_ramp_high, max_ramp_high)
                range_high = np.random.uniform (min_range_high, max_range_high)
                base_setpoint = houseSetpointDict[houseName] #np.random.uniform (min_base_setpoint, max_base_setpoint)
                ctrl_cap = np.random.uniform (min_ctrl_cap, max_ctrl_cap)
                initialVal['controller_information'] = {'control_mode': control_mode, 'aggregatorName': aggregatorName, 'houseName': controlledHouse, 'bid_id': controllerName, 'period': periodController, \
                           'ramp_low': ramp_low, 'ramp_high': ramp_high, 'range_low': range_low, 'range_high': range_high, 'base_setpoint': base_setpoint, \
                           'bid_delay': bid_delay, 'use_predictive_bidding': use_predictive_bidding, 'use_override': use_override, 'ctrl_cap': ctrl_cap, \
                           'hvac_load': hvacHouses[controlledHouse], 'heat_cool_gain': QhHouses[controlledHouse]
                           }
#                 initialVal['aggregator_information'] = {'market_id': 0, 'aggregator_unit': unit, 'initial_price': initial_price, 'average_price': initial_price, 'std_dev': std_dev, 'clear_price': initial_price, 'price_cap': price_cap, 'period': periodAggregator}
    
                # Finalize config dictionary
                config['subscriptions'] = subscriptions
                config['initial_value'] = initialVal
            
                # Store the config of this house into configAgg:
                HouseDict[houseName] = config
                configAgg['houses'].append(HouseDict)
                
                isNewAgg = False
                countHouse += 1


# Print the last group of controllers
# Write subscription to fncs_bridge message
configAgg['fncs_bridge'] = []
fncs_bridge = {}
fncs_bridge[fncs_zpl['name']] = {'propertyType': 'String', 'propertyUnit': 'none', 'propertyValue': 0}
configAgg['fncs_bridge'].append(fncs_bridge)

# Aggregator information initialization
configAgg['aggregator_information'] = {'market_id': 0, 'aggregator_unit': unit, 'initial_price': initial_price, 'average_price': initial_price, 'std_dev': std_dev, 'clear_price': initial_price, 'price_cap': price_cap, 'period': periodAggregator}

# data subscribed to aggregator
configAgg['aggregator'] = []
aggregator = {}
aggregator['market_id'] = {'type': 'integer', 'units': 'none', 'default': 1}
aggregator['initial_price'] = {'type': 'double', 'units': 'none', 'default': 0.0}
aggregator['average_price'] = {'type': 'double', 'units': 'none', 'default': 0.0}
aggregator['std_dev'] = {'type': 'double', 'units': 'none', 'default': 0.0}
aggregator['clear_price'] = {'type': 'double', 'units': 'none', 'default': 0.0}
aggregator['price_cap'] = {'type': 'double', 'units': 'none', 'default': 0.0}
configAgg['aggregator'].append({aggregatorNamePrev:aggregator})
aggregatorNamePrev = aggregatorName

# Write FNCS_VOLTTRON_Bridge configureation file
#                 write_FNCS_VOLTTRON_Bridge_Config(groupController, configAgg['houses'])

# Store all houses in the same group
allHouseDict[groupController] = []
houses = configAgg['houses']
for house in houses:
    name_temp = house.keys()
    if (len(name_temp) != 1):
        raise ValueError('The house key is more than 1')
    else:
        name_temp = name_temp[0]
        allHouseDict[groupController].append(name_temp)

# Write the controller configAgg information into one config file when reaching the group numbers defined:
print('At aggregated group ',groupController,' config files of all ',countHouse, ' houses controlled are written, with total hvac: ', aggHVAC)
filename = folderName + "/controller_" + str(groupController) + "_config.cfg"
op_controller = open(filename, "w")
json.dump(configAgg, op_controller)
op_controller.close()
groupController += 1
countHouse = 1
                
ip.close()

print("Finish writing controller config files based on fncs_configure.cfg")

# # Need to rearrange GLD config file
# ip = open (filename_conf, "r")
# op = open ('fncs_configure_cd.txt', "w")
# for line in ip:
#     if ('house' in line and 'FNCS_Volttron_Bridge' in line):
#         temp = line.split(':')
#         houseName = temp[1].split('.')[0]
#         for key, val in allHouseDict.items():
#             if houseName in val:
#                 break
#         replaceName = 'FNCS_Volttron_Bridge' + str(key)
#         line = line.replace('FNCS_Volttron_Bridge', replaceName)
#     op.write(line)
#     
# ip.close()
# op.close()
# 
# # Write bash file to run all FNCS_VOLTTRON_BRIDGE.py agents together
# folderName = "../FncsVolttronBridge"
# filename = folderName + '/runFNCS_VOLTTRON_BRIDGE.sh'
# op = open (filename, "w")
# numBridge = len(allHouseDict)
# for i in range(numBridge):
#     input = 'python FNCS_Volttron_Bridge.py ' + 'fncs/input' + str(i+1) + ' FNCS_VOLTTRON_Bridge' + str(i+1) + '.config ' + str(i+1) + ' &> FNCS_VOLTTRON_Bridge' + str(i+1) + '.log & \n'
#     op.write(input)
# op.close()





