import datetime
import logging
import sys
import uuid
import math
import numpy as np
from copy import deepcopy
import warnings
import csv

# import from ACOPF
import os
import time
import getopt
from AC_OPF_class import AC_OPF

#
from volttron.platform.vip.agent import Agent, Core, PubSub, compat
from volttron.platform.agent import utils
from volttron.platform.messaging import topics, headers as headers_mod

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '0.1'

def coordinator_agent(config_path, **kwargs):
    
    # Obtain the agent subscription and initial values from config file
    config = utils.load_config(config_path)
    agentSubscription = config['subscriptions']
    agentInitialVal = config['initial_value']
    mypath = "/home/yingying/git/volttron/TransactiveEnergy-ThreeAgg/CoordinatorAgent/coordinator/"
    
    class coordinatorAgent(Agent):
        '''This agent is the top level coordinator that collects the bidding curve from lower level aggregators and DERs before market clears.
        Then at the market clearing time, it sovles the circuit by conducting ACOPF, and obtain the cleared quantity.
        It will then calculate the cleared price at each bidding curve, and send back to cleared price down to aggregators, and quantity to DERs.
        '''
        def __init__(self, **kwargs):
            
            super(coordinatorAgent, self).__init__(**kwargs)
            
            self.startTime = datetime.datetime.now()
            _log.info('Simulation starts from: {0} in coordinator agent {1}.'.format(str(self.startTime), config['agentid']))
        
            # Initialize the variables
            self.market = {'name': 'none',' period': -1, 'latency': 0, 'market_id': 1, 'lastmkt_id': 1, 'period': 0, 'clearat': 0}  
            self.aggregator = {}
            self.aggregator_reactive = {}
            self.meters = {}
            self.meters_reactive = {}
            self.substation = {}
            self.substation_reactive = {}
            self.DERs = {} 
                       
            # Read and assign initial values from agentInitialVal
            # Market information
            self.market['name'] = config['agentid']
            self.market['bid_delay'] = agentInitialVal['market_information']['bid_delay']
            self.market['pricecap'] = agentInitialVal['market_information']['pricecap']
            self.market['period'] = agentInitialVal['market_information']['period']
            self.market['market_id'] = agentInitialVal['market_information']['market_id']
            self.market['lastmkt_id'] = self.market['market_id']
            # Aggregator information
            self.aggregator_info = agentInitialVal['aggregator_information']
            
#             self.market['period'] = 30 # For testing purpose only
            
            # Read in csv file storing total feeder loads without controllers and DGs
            fileName = agentInitialVal['market_information']['total_feeder_load']
            with open(mypath + fileName, 'rb') as f:
                reader = csv.reader(f)
                self.feederLoads = list(reader)
            
            # Aggregator information
            aggregators = agentSubscription['aggregators']
            for key1, value1 in aggregators[0].items():
                aggreName = key1
                self.aggregator[aggreName] = {}
                for key2, value2 in value1.items():
                    self.aggregator[aggreName][key2] = []
            
            aggregators = agentSubscription['aggregator_kVAR']
            for key, values in aggregators[0].items():
                aggreName = key
#                 self.aggregator_reactive[aggreName] = {}
                for key1, value1 in values.items():
                    self.aggregator_reactive[key1] = 0.0


            # Metered loads information
            meters = agentSubscription['metered_loads']
            for key, values in meters[0].items():
                meterName = key
                if ('substation' in meterName):
                    for key1, value1 in values.items():
                        if 'VAR' in key1:
                            self.substation_reactive = {key1: 0.0}
                        else:
                            self.substation = {key1: 0.0}  
                else:
                    for key1, value1 in values.items():
                        if 'VAR' in key1:
                            self.meters_reactive[key1] = 0.0
                        else:
                            self.meters[key1] = 0.0           
            
            # Metered DERs information
            DGs = agentSubscription['metered_DGs']
            for key1, values1 in DGs[0].items():
                DGName = key1
                self.DERs[DGName] = {}
                for key2, values2 in values1.items():
                    self.DERs[DGName][key2] = 0.0    
            
            # Check market period values assigned or not
            if self.market['period'] == 0:
                self.market['period'] = 300
                
            # Update bid delay:
            if self.market['bid_delay'] < 0:
                self.market['bid_delay'] = -self.market['bid_delay']
                
            if self.market['bid_delay'] > self.market['period']:
                warnings.warn('Bid delay is greater than the coordinator period. Resetting bid delay to 0.')
                self.market['bid_delay'] = 0
        
            ## Read and define subscription topics from agentSubscription     
            self.subscriptions = {}   
            self.subscriptions['aggregators'] = {}
            self.subscriptions['loads'] = {}
            self.subscriptions['substation'] = {}
            self.subscriptions['aggregators_kVAR'] = {}
            self.subscriptions['loads_kVAR'] = {}
            self.subscriptions['substation_kVAR'] = {}
            self.subscriptions['DERs'] = {}
            
             # subscription from aggregator
            for key, val in self.aggregator.items():
                topic = 'aggregator/' + key + '/biddings/all'
                self.subscriptions['aggregators'][key] = topic
            
            for key, val in self.aggregator_reactive.items():
                    topic = 'fncs/output/devices/fncs_Test/' + key
                    self.subscriptions['aggregators_kVAR'][key] = topic
                
            # subscription from metered loads in GLD
            for key, val in self.meters.items():
                topic = 'fncs/output/devices/fncs_Test/' + key
                self.subscriptions['loads'][key] = topic

            for key, val in self.meters_reactive.items():
                topic = 'fncs/output/devices/fncs_Test/' + key
                self.subscriptions['loads_kVAR'][key] = topic
            
            # subscription from substation loads in GLD
            for key, val in self.substation.items():
                topic = 'fncs/output/devices/fncs_Test/' + key
                self.subscriptions['substation'][key] = topic
            
            for key, val in self.substation_reactive.items():
                topic = 'fncs/output/devices/fncs_Test/' + key
                self.subscriptions['substation_kVAR'][key] = topic
            
            # subscription from metered DERs in GLD
            for key1, val1 in self.DERs.items():
                self.subscriptions['DERs'][key1] = []
                for key2, val2 in val1.items():
                    topic = 'fncs/output/devices/fncs_Test/' + key2
                    self.subscriptions['DERs'][key1].append(topic)
            
            # subscription from fncs_bridge
            self.subscriptions['fncs_bridge'] = []
            fncs_bridge = agentSubscription['fncs_bridge'][0]
            for key, val in fncs_bridge.items():
                topic = key + '/simulation_end'
                self.subscriptions['fncs_bridge'].append(topic)
            
            # Open csv file for recording cleared information during simulation
            self.csvCleared = config['agentid'] + '_cleared_information.csv'
            with open(self.csvCleared, 'w') as f:
                temp = ['Cleared_time', 'market_id', 'ACOPF_solved', 'cleared_price', 'cleared_quantity', 'cleared_DG1_output (kW)', 'cleared_DG2_output (kW)', 'social_welfare ($)', 'planned_SubstationP (kW)', 'expected_SubstationP (kW)', 'total_uncontrollable_loads']
                writer = csv.writer(f)
                writer.writerow(temp)
                f.flush()   
        
        @Core.receiver('onsetup')
        def setup(self, sender, **kwargs):
            self._agent_id = config['agentid']
            
        @Core.receiver('onstart')            
        def startup(self, sender, **kwargs):
            
            # Update the clear time 
            self.market['clearat'] = self.startTime + datetime.timedelta(0,self.market['period']) 
#             self.market['clearat'] = self.startTime + datetime.timedelta(0,10) # For testing
            
            # Initialize subscription function to aggregators
            for key, val in self.subscriptions['aggregators'].items():
                _log.info('Subscribing to ' + val)
                self.vip.pubsub.subscribe(peer='pubsub',
                                          prefix=val,
                                          callback=self.on_receive_aggregator_message)
            
            for key, val in self.subscriptions['aggregators_kVAR'].items():
                _log.info('Subscribing to ' + val)
                self.vip.pubsub.subscribe(peer='pubsub',
                                          prefix=val,
                                          callback=self.on_receive_aggregator_kVAR_message)
            
            # Initialize subscription function to metered loads
            for key, val in self.subscriptions['loads'].items():
                _log.info('Subscribing to ' + val)
                self.vip.pubsub.subscribe(peer='pubsub',
                                          prefix=val,
                                          callback=self.on_receive_load_message)
            
            for key, val in self.subscriptions['loads_kVAR'].items():
                _log.info('Subscribing to ' + val)
                self.vip.pubsub.subscribe(peer='pubsub',
                                          prefix=val,
                                          callback=self.on_receive_load_kVAR_message)
            
            # Initialize subscription function to metered substation
            for key, val in self.subscriptions['substation'].items():
                _log.info('Subscribing to ' + val)
                self.vip.pubsub.subscribe(peer='pubsub',
                                          prefix=val,
                                          callback=self.on_receive_substation_message)
            
            for key, val in self.subscriptions['substation_kVAR'].items():
                _log.info('Subscribing to ' + val)
                self.vip.pubsub.subscribe(peer='pubsub',
                                          prefix=val,
                                          callback=self.on_receive_substation_kVAR_message)
            
            # Initialize subscription function to metered DERs
            for key1, val1 in self.subscriptions['DERs'].items():
                for val2 in val1:
                    _log.info('Subscribing to ' + val2)
                    self.vip.pubsub.subscribe(peer='pubsub',
                                              prefix=val2,
                                              callback=self.on_receive_DER_message)
            
            # Initialize subscription function to fncs_bridge:
            for topic in self.subscriptions['fncs_bridge']:
                _log.info('Subscribing to ' + topic)
                self.vip.pubsub.subscribe(peer='pubsub',
                                          prefix=topic,
                                              callback=self.on_receive_fncs_bridge_message_fncs)
            
 
            
        # ====================extract float from string ===============================
        def get_num(self,fncs_string):
            return float(''.join(ele for ele in fncs_string if ele.isdigit() or ele == '.'))
        
        # ====================Obtain values from aggregator ===========================
        def on_receive_aggregator_message(self, peer, sender, bus, topic, headers, message):
            """Subscribe to aggregator publications and change the data accordingly 
            """    
            # Find the aggregator name who sends the message
            aggregatorName = topic.split("/")[-3]
            
            if ('VAR' not in aggregatorName):
                val = message[0]
                # Check if the market id from aggregator is the same as the coordinator
                if self.market['market_id'] == val['market_id']:
                                
                    _log.info('Coordinator {0:s} recieves from aggregator {1:s} the bids.'.format(self.market['name'], aggregatorName))
                
                    # Update bid data 
                    self.aggregator[aggregatorName]['price'] = val['price']
                    self.aggregator[aggregatorName]['quantity'] = val['quantity']
                    self.aggregator[aggregatorName]['name'] = val['name']
                else:
                    raise ValueError('The market id recieved from aggregator {0:d} is different from coordinator market id {1:d}'.format(val['market_id'], self.market['market_id']))
        
        def on_receive_aggregator_kVAR_message(self, peer, sender, bus, topic, headers, message):
            """Subscribe to GLD meter publications and change the data accordingly 
            """    
            # Find the metered load name
            aggregatorName = topic.split("/")[-1]
            
            val =  message[0]/1000  # Convert unit to kVAR
            
#             _log.info('At time {3:s},Coordinator {0:s} recieves from GLD the measured reactive power {1} kVAR at aggregator {2:s}.'.format(self.market['name'], val, aggregatorName, self.timeSim.strftime("%Y-%m-%d %H:%M:%S")))
            
            self.aggregator_reactive[aggregatorName] = val
            
        # ====================Obtain values from GLD metered load===========================
        def on_receive_load_message(self, peer, sender, bus, topic, headers, message):
            """Subscribe to GLD meter publications and change the data accordingly 
            """    
            # Find the metered load name
            meterName = topic.split("/")[-1]
            
            if ('VAR' not in meterName):
                val =  message[0]/1000  # Convert unit to kW
                
#                 _log.info('Coordinator {0:s} recieves from GLD the measured real power {1} kW at meter {2:s}.'.format(self.market['name'], val, meterName))
                
                self.meters[meterName] = val
        
        def on_receive_load_kVAR_message(self, peer, sender, bus, topic, headers, message):
            """Subscribe to GLD meter kVAR value publications and change the data accordingly 
            """    
            # Find the metered load name
            meterName = topic.split("/")[-1]
            val =  message[0]/1000  # Convert unit to kVAR
            
#             _log.info('Coordinator {0:s} recieves from GLD the measured reactive power {1} kVAR at meter {2:s}.'.format(self.market['name'], val, meterName))
            
            self.meters_reactive[meterName] = val
            
        # ====================Obtain values from GLD metered substation load===========================
        def on_receive_substation_message(self, peer, sender, bus, topic, headers, message):
            """Subscribe to GLD substation load publications and change the data accordingly 
            """    
            
            meterName = topic.split("/")[-1]
            
            if ('VAR' not in meterName):
                val =  message[0]/1000 # Convert unit to kW
                
#                 _log.info('Coordinator {0:s} recieves from GLD the measured real power {1} kW at substation.'.format(self.market['name'], val))
                
                self.substation[meterName] = val
        
        def on_receive_substation_kVAR_message(self, peer, sender, bus, topic, headers, message):
            """Subscribe to GLD substation load publications and change the data accordingly 
            """    
            
            meterName = topic.split("/")[-1]
            val =  message[0]/1000 # Convert unit to kVAR
            
#             _log.info('Coordinator {0:s} recieves from GLD the measured reactive power {1} kVAR at substation.'.format(self.market['name'], val))
            
            self.substation_reactive[meterName] = val
        
        # ====================Obtain values from GLD DER outputs===========================
        def on_receive_DER_message(self, peer, sender, bus, topic, headers, message):
            """Subscribe to GLD substation load publications and change the data accordingly 
            """    
            DERPhaseName = topic.split("/")[-1]
            DERName = DERPhaseName.split("_")[0] + '_'+ DERPhaseName.split("_")[1]
            phaseName = topic.split("/")[-1]
            val =  -message[0]/1000 # Convert unit to kW, and pay attention to sign. DG received should be negative
            
#             _log.info('Coordinator {0:s} recieves from GLD the measured real power {1} kW at substation.'.format(self.market['name'], val))
            
            self.DERs[DERName][DERPhaseName] = val
        
        # ====================Obtain utility price setpoint based on given quantity setpoint===========================
        def obtainUtility(self, val, ind, sumQuantityArray, UtilityArray):
            utilityPrice = 0.0
            
            if (ind == 0):
                utilityPrice = float(val * UtilityArray[ind] / sumQuantityArray[ind])
            else:
                q1 = sumQuantityArray[ind-1]
                q2 = sumQuantityArray[ind]
                x1 = UtilityArray[ind-1]
                x2 = UtilityArray[ind]
                utilityPrice = (val - q1) * (x2 - x1) / (q2 - q1) + x1
                utilityPrice = float(utilityPrice)
                
            return utilityPrice
        
        # ====================OBtain sorted price and quantity array from combined aggregator bids========================
        def sortBids(self, priceArray_Agg, quantityArray_Agg):
            
            # Test sort
#             priceArray_Agg = [6,5,4,3,9,8,4,2]
#             quantityArray_Agg = [1,2,1,3,1,3,5,1]
            index = sorted(range(len(priceArray_Agg)), key=lambda k: priceArray_Agg[k], reverse=True)
            priceArray_Agg = [priceArray_Agg[i] for i in index] 
            array_quantity = [quantityArray_Agg[i] for i in index] 
            returnArray = []
            returnArray.append(priceArray_Agg)
            returnArray.append(quantityArray_Agg)        
            
            return returnArray
        
        # ====================Obtain values from fncs_bridge ===========================
        def on_receive_fncs_bridge_message_fncs(self, peer, sender, bus, topic, headers, message):
            """Subscribe to fncs_bridge publications and change the data accordingly 
            """    

            val =  message[0] # value True
            if (val == 'True'):
                _log.info('Coordinator {0:s} recieves from fncs_bridge the siimulation ending signal.'.format(self.market['name']))
                self.core.stop() 
                
 
        @Core.periodic(1)
        def clear_market(self):
            ''' This method checks whether the market clearing time comes, and pre-process the data needed for ACOPF
            '''    
            # Update controller t1 information
            self.timeSim = datetime.datetime.now()               

            # Start market clearing process
            if self.timeSim >= self.market['clearat']:
                
                ## Process the aggregator data - buyer curve ------------------------------------------------------------------------------                
                uncontrolLds = {}
                priceArray = {}
                quantityArray = {}
                for key, value in self.aggregator.items(): # Currrently assume only one aggregator, or it will not work properly
                    uncontrolLds[key] = 0
                    priceArray[key] = []
                    quantityArray[key] = []
                    for i in range(len(value['price'])):
                        if value['price'][i] == self.market['pricecap']:
                            uncontrolLds[key] += value['quantity'][i]
                        else:
                            priceArray[key].append(value['price'][i])
                            quantityArray[key].append(value['quantity'][i])
                    quantityArray[key] = [x/1000.0 for x in quantityArray[key]] # unit should be MW in ACOPF 
#                 priceArray = [30, 20, 10] #value['price']
#                 quantityArray = [10, 10, 10] # value['quantity']
                
                # Rearrange aggregator bids based on accumulated aggregators on the same bus, if any
                lenAggre = len(self.aggregator_info)
                uncontrolLds_Agg = {}
                priceArray_Agg = {}
                quantityArray_Agg = {}
                for key, val in self.aggregator_info.items():
                    uncontrolLds_Agg[key] = 0
                    priceArray_Agg[key] = []
                    quantityArray_Agg[key] = []
                    for val1 in val:
                        uncontrolLds_Agg[key] += uncontrolLds[val1]
                        priceArray_Agg[key].extend(priceArray[val1])
                        quantityArray_Agg[key].extend(quantityArray[val1])
                    # Sort the combined aggregator bids in decsending order, if there are controllable bids
                    if len(priceArray_Agg[key]) != 0:
                        returnArrays = self.sortBids(priceArray_Agg[key], quantityArray_Agg[key])
                        priceArray_Agg[key] = returnArrays[0]
                        quantityArray_Agg[key] = returnArrays[1]
                    
                # Obtain DR array to be used by ACOPF
                self.DRquantity = []
                self.DRprice = []
                # Get several points from buyer bidding curve
                buyerCurveNum = 5 # Can be changed to other numbers
                for i in range(buyerCurveNum):
                    self.DRquantity.append(i+1)
                    self.DRprice.append(i+1)
                #
                if len(priceArray_Agg[key]) == 0:
                    # If only uncontrollable loads are existing in the buyer curves
                    self.DRquantity = ['18', '18', '18', '18', '18', '57', '57', '57', '57', '57', 1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    self.DRprice = ['18', '18', '18', '18', '18', '57', '57', '57', '57', '57', 1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
#                     self.DRquantity.extend([0] * buyerCurveNum)
#                     self.DRprice.extend([0] * buyerCurveNum)
                else:
                    # Or, grab several points with same steps
                    # The first item is always 0 by default in ACOPF 
                    self.DRquantity.extend(['18', '18', '18', '18', '18', '57', '57', '57', '57', '57', 1, 2, 3, 4, 5, 1, 2, 3, 4, 5])
                    self.DRprice.extend(['18', '18', '18', '18', '18', '57', '57', '57', '57', '57', 1, 2, 3, 4, 5, 1, 2, 3, 4, 5])
                    #
                    for key, val in self.aggregator_info:
                        priceArray = priceArray_Agg[key]
                        quantityArray = quantityArray_Agg[key]
                        # Grab the step points
                        step = sum(quantityArray)/(buyerCurveNum - 1)
                        UtilityArray = []
                        sumQuantityArray = []
                        sumUtility = 0
                        sumQuantity = 0
                        for i in range(len(quantityArray)):
                            sumUtility += quantityArray[i] * priceArray[i]
                            UtilityArray.append(sumUtility)
                            sumQuantity += quantityArray[i]
                            sumQuantityArray.append(sumQuantity)
                        for i in range(buyerCurveNum - 1):
                            val = step * (i + 1) # The value put into the DR quantity array, based on given number of points and corresponding step value
                            self.DRquantity.append(val)
                            for j in range(len(sumQuantityArray)):
                                if val <= sumQuantityArray[j]:
                                    utilityPrice = self.obtainUtility(val, j, sumQuantityArray, UtilityArray)
                                    self.DRprice.append(utilityPrice) # Put into the DRprice array based on quantity setpoint on the utility curve
                                    break;
                                elif val > sumQuantityArray[-1]:
                                    utilityPrice = self.obtainUtility(sumQuantityArray[-1], len(sumQuantityArray) - 1, sumQuantityArray, UtilityArray)
                                    self.DRprice.append(utilityPrice) # Put into the DRprice array based on quantity setpoint on the utility curve
                                    break;
                
                ## Obtain unknown bus real power ---------------------------------------------------------------------------------------------
                totalAggregatorLds = 0
                for key, value in self.aggregator.items():
                    totalAggregatorLds += sum(value['quantity'])
                totalDGoutputs = 0
                for key, value in self.DERs.items():
                    for key1, value1 in value.items():
                        totalDGoutputs += value1
                totalUnctlLds = 0
                for key, val in self.meters.items():
                    totalUnctlLds += val
                totalSubLds = 0
                for key, val in self.substation.items():
                    totalSubLds += val
                
                # Calculate unknown bus real power:
                unknownBusLds = totalSubLds + totalDGoutputs - (totalUnctlLds + totalAggregatorLds)
                
                # Record feeder information before conducting ACOPF                
                _log.info('At time {4}, coordinator agent {0} start computing ACOPF, with measured substation {1} MW, total DER outputs {2} MW, and controllable loads {3} MW'.format(config['agentid'], totalSubLds/1000.0, totalDGoutputs/1000.0, sum(quantityArray), self.timeSim.strftime("%Y-%m-%d %H:%M:%S")))
                 
                # Obtain unknown bus reactive power
                totalAggregatorLds = 0
                for key, value in self.aggregator_reactive.items():
                    totalAggregatorLds += value
                totalUnctlLds = 0
                for key, val in self.meters_reactive.items():
                    totalUnctlLds += val
                totalSubLdskVAR = 0
                for key, val in self.substation_reactive.items():
                    totalSubLdskVAR += val
                
                # Calculate unknown bus reactive power:
                unknownBusLds_kVAR = totalSubLdskVAR - (totalUnctlLds + totalAggregatorLds) 
                
                # Create list of P based on ACOPF fortmat requirement: ------------------------------------------------------------------------
                # Unit in MW
                bus7_P = unknownBusLds/1000.0
                bus18_P = uncontrolLds['bus_18']/1000.0 # Bus 18 includes uncontrollable loads from teh aggregator section
                bus57_P = uncontrolLds['bus_57']/1000.0
                Nbend = 3 # Defined in ACOPF
                Plist = [bus7_P, bus18_P, bus57_P] * 3
                self.P = [7, 18, 57]
                self.P.extend(Plist)
                
                # Create list of Q based on ACOPF fortmat requirement:
                # unit in MVAr
                bus7_Q = unknownBusLds_kVAR/1000.0
                bus18_Q = (self.aggregator_reactive['Aggregator_1'] + self.aggregator_reactive['Aggregator_2']) / 1000.0
                bus57_Q = self.aggregator_reactive['Aggregator_2'] / 1000.0
                Qlist = [bus7_Q, bus18_Q, bus57_Q] * 3
                self.Q = [7, 18, 57]
                self.Q.extend(Qlist)          
                
                # Calculate the time since simulation starts in second
                timeDiff = self.timeSim - self.startTime   
                timeDiffSec = timeDiff.days * 24 * 60 * 60 + timeDiff.seconds
                timeIndex = (timeDiffSec % (24 * 60 * 60) / 30) # index in total_feeder_load file
                feederLoad = float(self.feederLoads[timeIndex][0]) * 0.9 # Scale to 0.9 times of the original total loads
#                 feederLoad = totalSubLds / 1000.0 * 0.9 # Scale the DSO to be 0.9 of the amount needed from real-time substation loads
                
                # Clear the market by using the fixed_price sent from coordinator ---------------------------------------------------------------
                returnVal = self.ACOPF(feederLoad) 
                
#                 returnVal['solved'] = False # Hard corded for one case without any market involvment
                
                if returnVal['solved'] == True:
                    DERoutputs = returnVal['DER'] 
                    cleared_quantity = returnVal['DRquantity'] 
                    socialWelfare = returnVal['SocialWelfare']
                    subsPexpected = returnVal['substationP']
                else:
                    DERoutputs = [0, 0]
                    cleared_quantity = 0
                    socialWelfare = 0
                    subsPexpected = 0

                # Update lastmkt_id since the market just get cleared
                self.market['lastmkt_id'] = self.market['market_id']
                self.market['market_id'] += 1 # Go to wait for the next market

                # Publish cleared aggregator bidding price based on quantity solved by ACOPF               
                if len(priceArray) != 0 and returnVal['solved'] == True:
                    # When there are bids from aggregator (there are controllable loads)
                    clear_price = sumQuantityArray[-1]
                    for j in range(len(sumQuantityArray)):
                        if cleared_quantity <= sumQuantityArray[j]:
                            clear_price = priceArray[j]
                            break
                    # Publish clear_price
                    all_message = [{'market_id': self.market['market_id'], 
                        'fixed_price': clear_price, 
                        'no_bid': False                        
                        },
                       {'market_id': {'units': 'none', 'tz': 'UTC', 'type': 'integer'},
                        'fixed_price': {'units': '$', 'tz': 'UTC', 'type': 'float'},
                        'no_bid': {'units': 'none', 'tz': 'UTC', 'type': 'boolean'}                      
                        }]
                    pub_topic = 'coordinator/' + config['agentid'] + '/all'
                    _log.info('At time {2}, coordinator agent {0} with market_id {3} publishes updated cleared price {1} $ to aggregator agents based on cleared quanyity {4} kW'.format(config['agentid'], clear_price, self.timeSim.strftime("%Y-%m-%d %H:%M:%S"), self.market['market_id'], cleared_quantity * 1000))
                    # Create timestamp
                    now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
                    headers = {
                        headers_mod.DATE: now
                    }
                    self.vip.pubsub.publish('pubsub', pub_topic, headers, all_message)
                else:
                    # Publish clear_price
                    clear_price = 0.0
                    
                    all_message = [{'market_id': self.market['market_id'], 
                        'fixed_price': 0.0, 
                        'no_bid': True                        
                        },
                       {'market_id': {'units': 'none', 'tz': 'UTC', 'type': 'integer'},
                        'fixed_price': {'units': '$', 'tz': 'UTC', 'type': 'float'},
                        'no_bid': {'units': 'none', 'tz': 'UTC', 'type': 'boolean'}                      
                        }]
                    pub_topic = 'coordinator/' + config['agentid'] + '/all'
                    if returnVal['solved'] == True:
                        _log.info('At time {1}, coordinator agent {0} with market_id {2} publishes no_bid price 0.0 to aggregator agents since there are no bids recieved from controllable loads in this market period'.format(config['agentid'], self.timeSim.strftime("%Y-%m-%d %H:%M:%S"), self.market['market_id']))
                    else:
                        _log.info('At time {1}, coordinator agent {0} with market_id {2} publishes no_bid price 0.0 to aggregator agents since ACOPF could not be solved in this market period'.format(config['agentid'], self.timeSim.strftime("%Y-%m-%d %H:%M:%S"), self.market['market_id']))

                    # Create timestamp
                    now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
                    headers = {
                        headers_mod.DATE: now
                    }
                    self.vip.pubsub.publish('pubsub', pub_topic, headers, all_message)
                
                # Publish DER outputs
                if returnVal['solved'] == True:
                    if (len(DERoutputs) != len(self.DERs)):
                        raise ValueError('Length of ACOPF DER outputs {0} is not equal to the number of DERs {1} subscribed by coordinator'.format(len(DERoutputs), len(self.DERs)))
                    index = 0
                    for key1, val1 in self.DERs.items():
                        DERname = key1
                        DER_output = DERoutputs[index] * 1000000.0 / 3.0 # convert unit from MW to W
                        for key2, val2 in val1.items():
                            DER_phase_name = key2
                            # Publish the updated DER output by phase:
                            pub_topic = 'fncs/input/' + DER_phase_name
                            _log.info('At time {3}, coordinator agent {0} with market_id {3} publishes updated DER {1} output: {2}'.format(config['agentid'], DER_phase_name, DER_output, self.timeSim.strftime("%Y-%m-%d %H:%M:%S"), self.market['market_id']))
                            #Create timestamp
                            now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
                            headers = {
                                headers_mod.DATE: now
                            }
                            self.vip.pubsub.publish('pubsub', pub_topic, headers, -DER_output)
                        index += 1
                
                # TODOS: remove hard coding of DG outputs
                with open(self.csvCleared, 'a') as f:
                    temp = [self.timeSim.strftime("%Y-%m-%d-%H:%M:%S"), str(self.market['market_id']), str(returnVal['solved']), str(clear_price), str(cleared_quantity * 1000.0), str(DERoutputs[0] * 1000.0), str(DERoutputs[1] * 1000.0), str(socialWelfare), str(feederLoad * 1000), str(subsPexpected * 1000.0), (bus7_P + bus18_P + bus57_P) * 1000]
                    writer = csv.writer(f)
                    writer.writerow(temp)
                    f.flush()
                    
                # Display the opening of the next market
                tiemDiff = (self.timeSim + datetime.timedelta(0,self.market['period']) - self.market['clearat']).total_seconds() % self.market['period']
#                 self.market['clearat'] = self.timeSim + datetime.timedelta(0,self.market['period'] - tiemDiff)
                self.market['clearat'] = self.market['clearat'] + datetime.timedelta(0,self.market['period'])

                
        
        # ======================== Conduct ACOPF by calling GAMS ==============    
        def ACOPF(self, feederLoad):
            # Call GAMS to conduct ACOPF
            system = "7bus"
            
            # get options from python call --------------------------------------------
            try:
                opts, args = getopt.getopt(
                    [],
                    "hn:s:v:d:b:c:a:r:u:t:p:f:b:",
                    ["help",
                     "num_time_steps",
                     "shuntSwitchingPenalty1",
                     "load_bus_voltage_goal",
                     "solar_off",
                     "control_load_off",
                     "solar_q_off",
                     "shunt_switching_off",
                     "load_bus_volt_dead_band",
                     "load_bus_volt_pen_coeff_1",
                     "load_bus_volt_pen_coeff_2",
                     "previous_solution_as_start_point"
                     "file_number"
                     "debug_start_from_certan_point"])
            except getopt.GetoptError:
                usage()
                sys.exit(2)
            for opt, arg in opts:
                if opt in ("-h", "--help"):
                    usage()
                    sys.exit()
                elif opt in ("-n", "--num_time_steps"):
                    Nbend = int(arg) 
                elif opt in ("-s", "--shuntSwitchingPenalty1"):
                    shuntSwitchingPenalty1 = float(arg)
                elif opt in ("-v", "--load_bus_voltage_goal"):
                    load_bus_voltage_goal = float(arg)
                elif opt in ("-d", "--solar_off"):
                    solar_off = int(arg)
                elif opt in ("-b", "--control_load_off"):
                    control_load_off = int(arg)
                elif opt in ("-c", "--solar_q_off"):
                    solar_q_off = int(arg)
                elif opt in ("-a", "--shunt_switching_off"):
                    shunt_switching_off = int(arg)
                elif opt in ("-r", "--load_bus_volt_dead_band"):
                    load_bus_volt_dead_band = float(arg)
                elif opt in ("-u", "--load_bus_volt_pen_coeff_1"):
                    load_bus_volt_pen_coeff_1 = float(arg)
                elif opt in ("-t", "--load_bus_volt_pen_coeff_2"):
                    load_bus_volt_pen_coeff_2 = float(arg)
                elif opt in ("-p", "--previous_solution_as_start_point"):
                    previous_solution_as_start_point = int(arg)
                elif opt in ("-f", "--file_number"):
                    fileorder = int(arg)   
                elif opt in ("-b", "--debug_start_from_certan_point"):
                    startrow = int(arg)  
            # -------------------------------------------------------------------------
            
            # Calculate the program running time
            ACOPF_start_time = time.time()  
            
            # For Editing Excel
            if os.path.isfile("switched_shunt_current.gdx"):
                os.remove("switched_shunt_current.gdx")           
            # Temporary invalid for test purpose
            if os.path.isfile("one_step_solution.gdx"):
                os.remove("one_step_solution.gdx")
            
        
            try:
                    
                if system == "7bus":
                    # 118-BUS SYSTEM PARAMETERS ----------------------------------------------
                    system_folder                           = mypath + '7bus'
                    sum_bus_num                             = 7
                    sum_load_num                            = 3
                    sum_gennum                              = 1 
                    # Define the location of solar bus and solar apparent power
                    definegenlocation                       = True
                    sum_distributed_gen                     = 2
                    control_load_BusID                      = 18    
                    solar_qlimit_busID                      = 18
                    # Nbend is for the number of steps we'd like to run
                    Nbend                                   = 1 #(12*duration[hour]+1)  
                    # Define start row
                    startrow                                = 2   #(12*stating_hour+1)    
                    Nbend2                                  = 5
                    #nbend2 is the column of the price signal    
                    # file order specify the date    W
                    fileorder                               = 1
                    simuyear                                = 2006
                    simutimestep                            = 5
                    GDXcaseName                             = '7bus.gdx'
                    # Time-stamp in the input excel file? (this option is temporary)
                    TimeStamp                               = False
                    solar_curtail_busid                     = 84
                    #-------------------------------------------------------------------------
                    
                else:
                    assert False, "specify system in main python code"
        
            except NameError:
                assert False, "specify system in main python code"
        
         
            ## OPTIMIZATION PROBLEM PARAMETERS ----------------------------------------
            load_bus_voltage_goal                   = 1.0
            solar_curtailment_off                   = 1
            control_load_off                        = 0
            solar_q_off                             = 0
            shunt_switching_off                     = 1
            previous_solution_as_start_point        = 0 
            # Penalty terms
            shuntSwitchingPenalty1                  = 1e-3
            demand_response_decrease_penalty        = 10
            demand_response_increase_penalty        = 10
            solar_curtail_penalty                   = 50
            generator_voltage_deviation_penalty     = 1e5
            load_bus_volt_pen_coeff_1               = 1
            load_bus_volt_pen_coeff_2               = 0
            load_bus_volt_dead_band                 = 1e-2
        
            # can use values 0,1,2,3,9, where 0 start from last solution point, 1 from random all, 2 from flat start, 3 is random voltage, 9 is for given starting point
            icset                                   = [9, 2, 9, 3, 1, 0, 0, 0]    
            max_iter                                = 4
            # Control voltage of generators and loads at scheduled values or not
            opt_Vgen_dev                            = 1
            opt_Vload_dev                           = 1        
            # -------------------------------------------------------------------------    

            
            ## OPTIONS FOR PLOTTING RESULTS -------------------------------------------
            # export the result to spreadsheet or not
            export_to_spreadsheet                   = True
        
            # -------------------------------------------------------------------------
                        
            # Input excel files
            bus_list_file                           = 'bus_list.xlsx'      
            distrb_gen_index_file                   = 'distribu_index2.xlsx'
            solar_oneyear_file                      = 'solar_s_oneyeartest.xlsx'
            GAMS_OptionSolution_GDXfile             = "one_step_solution.gdx"
            demand_response_file                    = 'demand_response_load_price.xlsx'
            GAMS_OPF_file                           = "iv_acopf_reformulation_lop_adj.gms"    
             
        
            """ CALL AC_OPF object"""                    
            System = AC_OPF(Nbend, Nbend2, fileorder, simuyear, simutimestep, startrow, definegenlocation, sum_bus_num, sum_load_num, sum_gennum, sum_distributed_gen,\
                            solar_curtail_busid, control_load_BusID,solar_qlimit_busID, load_bus_voltage_goal, solar_curtailment_off, control_load_off, solar_q_off, shunt_switching_off,\
                            shuntSwitchingPenalty1, demand_response_decrease_penalty, demand_response_increase_penalty, solar_curtail_penalty, generator_voltage_deviation_penalty,\
                            load_bus_volt_pen_coeff_1, load_bus_volt_pen_coeff_2, load_bus_volt_dead_band, opt_Vgen_dev, opt_Vload_dev, previous_solution_as_start_point, icset, max_iter,\
                            bus_list_file, distrb_gen_index_file, solar_oneyear_file, GAMS_OptionSolution_GDXfile, GAMS_OPF_file, demand_response_file,\
                            export_to_spreadsheet, system_folder, GDXcaseName, TimeStamp, feederLoad, self.P, self.Q, self.DRquantity, self.DRprice)
        
            
            _log.info("--- ACOPF total running time: %s seconds ---" % (time.time() - ACOPF_start_time))
            
            return System.returnVal
        
                      
    Agent.__name__ = config['agentid']
    return coordinatorAgent(**kwargs)        
                
def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(coordinator_agent)
    except Exception as e:
        print e
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
                         