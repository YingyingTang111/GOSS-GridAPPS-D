import datetime
import logging
import sys
import uuid
import math
import numpy as np
from copy import deepcopy
import warnings
import csv
import json

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
            self.subscriptions = {} 
                       
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
            # DER index in ACOPF solution
            self.DERinfo = agentInitialVal['DER_information']
            
            self.market['period'] = 30 # For testing purpose only
            
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
            self.subscriptions['aggregators_kVAR'] = {}
            for key, values in aggregators[0].items():
#                 self.aggregator_reactive[aggreName] = {}
                for key1, value1 in values.items():
                    self.aggregator_reactive[key1] = 0.0
                    for key2, value2 in value1.items():
                        self.subscriptions['aggregators_kVAR'][key1] = key2 # give the meter and property name to be subscribed


            # Metered loads information
            meters = agentSubscription['metered_loads']
            self.subscriptions['substation'] = {}
            self.subscriptions['substation_kVAR'] = {}
            for key, values in meters[0].items():
                meterName = key
                if ('substation' in meterName):
                    for key1, value1 in values.items():
                            for key2, value2 in value1.items():
                                if 'reactive' in key2:
                                    self.substation_reactive = {key1: 0.0}
                                    self.subscriptions['substation_kVAR'][key1] = key2

                                else: 
                                    self.substation = {key1: 0.0} 
                                    self.subscriptions['substation'][key1] = key2
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
            self.subscriptions['aggregators'] = {}
            self.subscriptions['DERs'] = {}
            
             # subscription from aggregator
            for key, val in self.aggregator.items():
                topic = 'aggregator/' + key + '/biddings/all'
                self.subscriptions['aggregators'][key] = topic
            
            # subscription from metered DERs in GLD
            for key1, val1 in self.DERs.items():
                self.subscriptions['DERs'][key1] = []
                for key2, val2 in val1.items():
                    # topic = 'fncs/output/devices/fncs_Test/' + key2
                    self.subscriptions['DERs'][key1].append(key2)
            
            # subscription from fncs_bridge
            self.subscriptions['fncs_bridge'] = []
            fncs_bridge = agentSubscription['fncs_bridge'][0]
            for key, val in fncs_bridge.items():
                topic = key + '/simulation_end'
                self.subscriptions['fncs_bridge'].append(topic)
            
            # Open csv file for recording cleared information during simulation
            self.csvCleared = config['agentid'] + '_cleared_information.csv'
            with open(self.csvCleared, 'w') as f:
                temp = ['Cleared_time', 'market_id', 'ACOPF_solved', 'cleared_price', 'cleared_quantity', 'DG_152_output (kW)', 'DG_7_output (kW)', 'DG_18_output (kW)', 'DG_56_output (kW)', 'DG_57_output (kW)', 'social_welfare ($)', 'planned_SubstationP (kW)', 'expected_SubstationP (kW)', 'total_uncontrollable_loads']
                writer = csv.writer(f)
                writer.writerow(temp)
                f.flush()   
        
        @Core.receiver('onsetup')
        def setup(self, sender, **kwargs):
            self._agent_id = config['agentid']
            
        @Core.receiver('onstart')            
        def startup(self, sender, **kwargs):
            
            # Update the clear time 
#             self.market['clearat'] = self.startTime + datetime.timedelta(0,self.market['period']) 
            self.market['clearat'] = self.startTime + datetime.timedelta(0,10) # For testing

            # Initialize subscription function to GLD meter:
            # Subscription to houses in GridLAB-D needs to post-process JSON format messages of all GLD objects together
            subscription_topic = 'fncs/output/devices/fncs_Test/fncs_output'
            _log.info('Subscribing to ' + subscription_topic)
            self.vip.pubsub.subscribe(peer='pubsub',
                                      prefix=subscription_topic,
                                      callback=self.on_receive_GLD_message_fncs)
            
            # Initialize subscription function to aggregators
            for key, val in self.subscriptions['aggregators'].items():
                _log.info('Subscribing to ' + val)
                self.vip.pubsub.subscribe(peer='pubsub',
                                          prefix=val,
                                          callback=self.on_receive_aggregator_message)
                                          
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
        
        # ====================Obtain values from GLD ===========================
        def on_receive_GLD_message_fncs(self, peer, sender, bus, topic, headers, message):
            """Subscribe to GLD publications and change the data accordingly 
            """                
            # Recieve from GLD the property values of all configured objects, need to extract the house objects and the corresponding properties
            # Extract the message
            message = json.loads(message[0])
            valFNCS =  message['fncs_Test']
            # Check each subscribed objects from GLD
            # substation real power
            for key, val in self.subscriptions['substation'].items():
                valTemp = float(valFNCS[key][val])/1000 # Convert unit to kW
                if valTemp != self.substation[key]:
                    self.substation[key] = valTemp
                    
            # substation reactive power
            for key, val in self.subscriptions['substation_kVAR'].items():
                valTemp = float(valFNCS[key][val])/1000 # Convert unit to kVAR
                if valTemp != self.substation_reactive[key]:
                    self.substation_reactive[key] = valTemp
                    
            # DG real power
            for key, val in self.subscriptions['DERs'].items():
                for val2 in val:
                    valTemp = -float(valFNCS[key][val2])/1000 # Convert unit to kW, and pay attention to sign. DG received should be negative
                    if valTemp != self.DERs[key][val2]:
                        self.DERs[key][val2] = valTemp
                        
            # aggregated reactive power
            for key, val in self.subscriptions['aggregators_kVAR'].items():
                valTemp = float(valFNCS[key][val])/1000 # Convert unit to kVAR
                if valTemp != self.subscriptions['aggregators_kVAR'][key]:
                    self.aggregator_reactive[key] = valTemp
        
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
            returnArray.append(array_quantity)        
            
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
            buyerCurveNum = 5 # Can be changed to other numbers       

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

                # ================= test ==============================
#                 priceArray['Aggregator_1'] = [38.44660063525528]
#                 quantityArray['Aggregator_1'] = [5.27426723538]
#                 priceArray['Aggregator_2'] = [38.7160865156434, 34.802772434443206]
#                 quantityArray['Aggregator_2'] = [3.3991152471, 4.9151141704]
#                 priceArray['Aggregator_3'] = [48.03168983721315, 45.7787032506492, 38.86561072789027, 38.38057600631638]
#                 quantityArray['Aggregator_3'] = [3.04079978203, 3.41805469253, 4.14582476689, 4.13504898077]
                # =====================================================
                
                # Rearrange aggregator bids based on accumulated aggregators on the same bus, if any
                lenAggre = len(self.aggregator_info)
                uncontrolLds_Agg = {}
                priceArray_Agg = {}
                quantityArray_Agg = {}
                self.DRquantity = []
                self.DRprice = []
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
                    # Start wring DR list
                    busName = key.replace('bus_', '')
                    self.DRquantity.extend([busName] * buyerCurveNum)
                    self.DRprice.extend([busName] * buyerCurveNum)
                    
                self.DRquantity.extend(range(1, buyerCurveNum + 1) * 2)
                self.DRprice.extend(range(1, buyerCurveNum + 1) * 2)
                    
                
                # Get several points from buyer bidding curve
                for i in range(buyerCurveNum):
                    self.DRquantity.append(i+1)
                    self.DRprice.append(i+1)
                    
                # Check whether at each aggregated bus there are bids
                # Obtain DR array to be used by ACOPF
                length_bids = {key: len(value) for key, value in priceArray_Agg.items()}
                DRquantityTemp = []
                DRpriceTemp = []
                for key, val in self.aggregator_info.items():
                    if length_bids[key] == 0:
                        # If there is no bids on this bus, put zeros to DR list
                        self.DRquantity.extend([0] * buyerCurveNum)
                        self.DRprice.extend([0] * buyerCurveNum)
                    else:
                        # Or, grab several points with same steps
                        # The first item is always 0 by default in ACOPF 
                        self.DRprice.append(0)
                        self.DRquantity.append(0)
                        #
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
                
                totalCtlLds = 0
                for key in quantityArray_Agg:
                    if len(quantityArray_Agg[key]) != 0:
                        totalCtlLds += sum(quantityArray_Agg[key])
                
                # Record feeder information before conducting ACOPF                
                _log.info('At time {4}, coordinator agent {0} start computing ACOPF, with measured substation {1} MW, total DER outputs {2} MW, and controllable loads {3} MW'.format(config['agentid'], totalSubLds/1000.0, totalDGoutputs/1000.0, totalCtlLds, self.timeSim.strftime("%Y-%m-%d %H:%M:%S")))
                 
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
                bus18_P = uncontrolLds_Agg['bus_18']/1000.0 # Bus 18 includes uncontrollable loads from teh aggregator section
                bus57_P = uncontrolLds_Agg['bus_57']/1000.0
                Nbend = 3 # Defined in ACOPF
                Plist = [bus7_P, bus18_P, bus57_P] * 3
                self.P = [7, 18, 57]
                self.P.extend(Plist)
                
                # Create list of Q based on ACOPF fortmat requirement:
                # unit in MVAr
                bus7_Q = unknownBusLds_kVAR/1000.0
                bus18_Q = (self.aggregator_reactive['Meter_18_21'] + self.aggregator_reactive['Meter_18_135']) / 1000.0
                bus57_Q = self.aggregator_reactive['Meter_57_60'] / 1000.0
                Qlist = [bus7_Q, bus18_Q, bus57_Q] * 3
                self.Q = [7, 18, 57]
                self.Q.extend(Qlist)          
                
                # Calculate the time since simulation starts in second
                timeDiff = self.timeSim - self.startTime   
                timeDiffSec = timeDiff.days * 24 * 60 * 60 + timeDiff.seconds
                timeIndex = (timeDiffSec % (24 * 60 * 60) / 30) # index in total_feeder_load file
                feederLoad = float(self.feederLoads[timeIndex][0]) * 0.9 # Scale to 0.9 times of the original total loads
#                 feederLoad = totalSubLds / 1000.0 * 0.9 # Scale the DSO to be 0.9 of the amount needed from real-time substation loads

                
                for key1, val1 in self.DERs.items():
                    DERname = key1
                    index = self.DERinfo[DERname] # Find the DER index in ACOPF solution
#                     DER_output = DERoutputs[index] * 1000000.0 / 3.0 # convert unit from MW to W
                    for key2, val2 in val1.items():
                        DER_phase_name = key2
                        # Publish the updated DER output by phase:
                        pub_topic = 'fncs/input/' + DERname + '/' + DER_phase_name
                        _log.info('At time {3}, coordinator agent {0} with market_id {3} publishes updated DER {1} output: {2}'.format(config['agentid'], DER_phase_name, 1000000, self.timeSim.strftime("%Y-%m-%d %H:%M:%S"), self.market['market_id']))
                        #Create timestamp
                        now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
                        headers = {
                            headers_mod.DATE: now
                        }
                        self.vip.pubsub.publish('pubsub', pub_topic, headers, -1000000.00)

                    
                # Display the opening of the next market
                tiemDiff = (self.timeSim + datetime.timedelta(0,self.market['period']) - self.market['clearat']).total_seconds() % self.market['period']
#                 self.market['clearat'] = self.timeSim + datetime.timedelta(0,self.market['period'] - tiemDiff)
                self.market['clearat'] = self.market['clearat'] + datetime.timedelta(0,self.market['period'])

        
                      
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
                         