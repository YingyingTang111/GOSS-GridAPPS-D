import datetime
import logging
import sys
import uuid
import math
import numpy as np
from copy import deepcopy
import warnings

from get_curve import curve

from volttron.platform.vip.agent import Agent, Core, PubSub, compat
from volttron.platform.agent import utils
from volttron.platform.messaging import topics, headers as headers_mod

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '0.1'

def aggregator_agent(config_path, **kwargs):
    
    # Obtain the agent subscription and initial values from config file
    config = utils.load_config(config_path)
    agentSubscription = config['subscriptions']
    agentInitialVal = config['initial_value']
    
    class aggregatorAgent(Agent):
        '''This agent is the middle level aggregator that collects the bid from lower level controller agent,
        and send the accumulated bid curve to the upper level coordinator agent before market clears. 
        After market clears in coordinator agent, it recives the cleared price, and send back to its lower level controller agents.
        '''
        def __init__(self, **kwargs):
            
            super(aggregatorAgent, self).__init__(**kwargs)
            
            self.startTime = datetime.datetime.now()
            _log.info('Simulation starts from: {0} in aggregator agent {1}.'.format(str(self.startTime), config['agentid']))
        
            # Initialize the variables
            self.stats = {'stat_mode': [], 'interval': [], 'stat_type': [], 'value': [], 'statistic_count': 0}
            self.market = {'name': 'none',' period': -1, 'latency': 0, 'market_id': 0, 'network': 'none', 'linkref': 'none', 'pricecap': 0.0, 'bid_delay': 10,
                           'special_mode': 'MD_NONE', 'statistic_mode': 1, 'fixed_price': 50.0, 'fixed_quantity': 0.0,
                           'init_price': 0.0, 'init_stdev': 0.0, 'future_mean_price': 0.0, 'use_future_mean_price': 0, 
                           'capacity_reference_object': {'name': 'none', 'capacity_reference_property': 0.0, 'capacity_reference_bid_price': 0.0, 
                                                         'max_capacity_reference_bid_quantity': 0.0, 'capacity_reference_bid_quantity': 0.0},
                           'current_frame': {'start_time': 0.0, 'end_time': 0.0, 'clearing_price':0.0, 'clearing_quantity': 0.0, 'clearing_type': 'CT_NULL', 
                                              'marginal_quantity': 0.0, 'total_marginal_quantity': 0.0, 'marginal_frac': 0.0, 'seller_total_quantity': 0.0, 
                                              'buyer_total_quantity': 0.0, 'seller_min_price': 0.0, 'buyer_total_unrep': 0.0, 'cap_ref_unrep': 0.0, 
                                              'statistics': []}, 
                           'past_frame': {'start_time': 0.0, 'end_time': 0.0, 'clearing_price':0.0, 'clearing_quantity': 0.0, 'clearing_type': 'CT_NULL', 
                                              'marginal_quantity': 0.0, 'total_marginal_quantity': 0.0, 'marginal_frac': 0.0, 'seller_total_quantity': 0.0, 
                                              'buyer_total_quantity': 0.0, 'seller_min_price': 0.0, 'buyer_total_unrep': 0.0, 'cap_ref_unrep': 0.0, 
                                              'statistics': []}, 
                           'cleared_frame': {'start_time': 0.0, 'end_time': 0.0, 'clearing_price':0.0, 'clearing_quantity': 0.0, 'clearing_type': 'CT_NULL', 
                                              'marginal_quantity': 0.0, 'total_marginal_quantity': 0.0, 'marginal_frac': 0.0, 'seller_total_quantity': 0.0, 
                                              'buyer_total_quantity': 0.0, 'seller_min_price': 0.0, 'buyer_total_unrep': 0.0, 'cap_ref_unrep': 0.0, 
                                              'statistics': []}, 
                           'margin_mode': 'AM_NONE', 'ignore_pricecap': 0,'ignore_failedmarket': 0, 'warmup': 1,
                           'total_samples': 0,'clearat': 0,  'clearing_scalar': 0.5, 'longest_statistic': 0.0}  
                
            self.market_output = {'std': -1, 'mean': -1, 'clear_price': -1, 'market_id': 'none', 'pricecap': 0.0} # Initialize market output with default values
            self.buyer = {'name': [], 'price': [], 'quantity': [], 'state': [], 'bid_id': []}
            self.seller = {'name': [], 'price': [], 'quantity': [], 'state': [], 'bid_id': []} 
            self.nextClear = {'from':0, 'quantity':0, 'price':0}
            self.offers = {'name': [], 'price': [], 'quantity': []}           
            
            self.market['name'] = config['agentid']
            
            # Read and assign initial values from agentInitialVal
            # Market information
            self.market['special_mode'] = agentInitialVal['market_information']['special_mode']
            self.market['bid_delay'] = agentInitialVal['market_information']['bid_delay']
            self.market['market_id'] = agentInitialVal['market_information']['market_id']
            self.market['use_future_mean_price'] = agentInitialVal['market_information']['use_future_mean_price']
            self.market['pricecap'] = agentInitialVal['market_information']['pricecap']
            self.market['clearing_scalar'] = agentInitialVal['market_information']['clearing_scalar']
            self.market['period'] = agentInitialVal['market_information']['period']
            self.market['latency'] = agentInitialVal['market_information']['latency']
            self.market['init_price'] = agentInitialVal['market_information']['init_price']
            self.market['fixed_price'] = agentInitialVal['market_information']['fixed_price']
            self.market['init_stdev'] = agentInitialVal['market_information']['init_stdev']
            self.market['ignore_pricecap'] = agentInitialVal['market_information']['ignore_pricecap']
            self.market['ignore_failedmarket'] = agentInitialVal['market_information']['ignore_failedmarket']
            self.market['statistic_mode'] = agentInitialVal['market_information']['statistic_mode']
            self.market['capacity_reference_object']['name'] = agentInitialVal['market_information']['capacity_reference_object']
            self.market['capacity_reference_object']['max_capacity_reference_bid_quantity'] = agentInitialVal['market_information']['max_capacity_reference_bid_quantity']
            self.market['lastmkt_id'] = self.market['market_id']
            
            # Stats information
            self.stats['stat_mode'] = agentInitialVal['statistics_information']['stat_mode']
            self.stats['interval'] = agentInitialVal['statistics_information']['interval']
            self.stats['stat_type'] = agentInitialVal['statistics_information']['stat_type']
            self.stats['value'] = agentInitialVal['statistics_information']['value']
            
            # Controller information
            self.controller = {'name': [], 'price': [], 'quantity': [], 'state': []}
            self.controller['name'] = agentInitialVal['controller_information']['name']
            self.controller['price'] = agentInitialVal['controller_information']['price']
            self.controller['quantity'] = agentInitialVal['controller_information']['quantity']
            self.controller['state'] = agentInitialVal['controller_information']['state']
            
            # Coordinator information
            self.coordinator = {'market_id':-1, 'fixed_price':-1, 'received': False}
            
            # Update market data based on given stats data
            self.market['statistic_count'] = len(self.stats['stat_mode'])
            self.market['longest_statistic'] = max(self.stats['interval'])
            
            # Give the updated mean and std values to the market_output        
            if self.market['statistic_mode'] == 1:
                for k in range(0, len(self.stats['value'])):
                    if self.stats['stat_type'][k] == 'SY_MEAN':
                        self.market_output['mean'] = self.stats['value'][k]
                    elif self.stats['stat_type'][k] == 'SY_STDEV':
                        self.market_output['std'] = self.stats['value'][k]
    
            
            # Initialization when time = 0    
            # Check market pricap values assigned or not
            if self.market['pricecap'] == 0.0:
                self.market['pricecap'] = 9999.0
            
            # Check market period values assigned or not
            if self.market['period'] == 0:
                self.market['period'] = 300
                
            # Update bid delay:
            if self.market['bid_delay'] < 0:
                self.market['bid_delay'] = -self.market['bid_delay']
                
            if self.market['bid_delay'] > self.market['period']:
                warnings.warn('Bid delay is greater than the aggregator period. Resetting bid delay to 0.')
                self.market['bid_delay'] = 0
            
            # Check market latency values assigned or not
            if self.market['latency'] < 0:
                self.market['latency'] = 0
            
            # Check the statistic period
            for i in range(0, len(self.stats['interval'])):
                if self.stats['interval'][i] < self.market['period']:
                    warnings.warn('market statistic samples faster than the market updates and will be filled with immediate data')
                    
                if self.stats['interval'][i] % float(self.market['period']) != 0:
                    warnings.warn('market statistic  interval not a multiple of market period, rounding towards one interval')
                    self.stats['interval'][i] = self.stats['interval'][i] - (self.stats['interval'][i] % float(self.market['period']))
                   
            # Check special mode
            if self.market['special_mode'] != 'MD_NONE' and self.market['fixed_quantity'] < 0.0:
                raise ValueError('Auction is using a one-sided market with a negative fixed quantity')
            
            # Initialize latency queue
            self.market['latency_count'] = int (self.market['latency'] / self.market['period']) + 2
            self.market['framedata'] = [[] for i in range(self.market['latency_count'])]  
            self.market['latency_front'] = self.market['latency_back'] = 0
                
            # Assign new keys and values to the market
            if self.market['longest_statistic'] > 0: 
                self.market['history_count'] = int(self.market['longest_statistic'] / self.market['period']) + 2
                self.market['new_prices'] = self.market['init_price']*np.ones(self.market['history_count'])
                self.market['new_market_failures'] = ['CT_EXACT']*self.market['history_count']
            else:
                self.market['history_count'] = 1
                self.market['new_prices'] = self.market['init_price']
                self.market['new_market_failures'] = 'CT_EXACT'
                
            self.market['price_index'] = self.market['price_count'] = 0
            
            if self.market['init_stdev'] < 0.0:
                raise ValueError('auction init_stdev is negative!')
                
            # Assign initial values to the market outputs
            self.market_output['std'] = self.market['init_stdev']
            self.market_output['mean'] = self.market['init_price']
            
            if self.market['clearing_scalar'] <= 0.0:
                self.market['clearing_scalar'] = 0.5
            elif self.market['clearing_scalar'] >= 1.0:
                self.market['clearing_scalar'] = 0.5
            
            self.market['current_frame']['clearing_price'] = self.market['past_frame']['clearing_price'] = self.market['init_price']  
            
            ## Read and define subscription topics from agentSubscription     
            self.subscriptions = {}   
            self.subscriptions['controller'] = []
            self.subscriptions['meter'] = []
            self.subscriptions['fncs_bridge'] = []
            self.subscriptions['coordinator'] = []
            # Check agentSubscription
            controller = agentSubscription['controller'][0]
            if len(controller) < 1:
                raise ValueError('The aggregator is defined to control 0 controller, which is not correct')
            meter = agentSubscription['meter'][0]
            if len(meter) != 1:
                raise ValueError('The aggregator is defined to be located at more/less than one meter (switch), which is not correct')
             # subscription from controller
            for key, val in controller.items():
                topic = 'controller/' + key + '/all'
                self.subscriptions['controller'].append(topic)
            # subscription from aggregator agent
            for key, val in meter.items():
                topic = 'fncs/output/devices/fncs_Test/' + key
                self.subscriptions['meter'].append(topic)
            # subscription from fncs_bridge
            fncs_bridge = agentSubscription['fncs_bridge'][0]
            for key, val in fncs_bridge.items():
                topic = key + '/simulation_end'
                self.subscriptions['fncs_bridge'].append(topic)
            # subscription from coordinator agent
            coordinatorAgent = agentSubscription['coordinator'][0]
            for key, val in coordinatorAgent.items():
                topic = 'coordinator/' + key + '/all'
                self.subscriptions['coordinator'].append(topic)
            
            # Create JSON file storing controller bids and cleared information from coordinator
            controller_bids_meta = {'bid_price':{'units':'USD','index':0},'bid_quantity':{'units':'kW','index':1}}
            self.controller_bids_metrics = {'Metadata':controller_bids_meta,'StartTime':self.startTime.strftime("%Y-%m-%d %H:%M:%S")}
            aggregator_cleared_meta = {'clearing_price':{'units':'USD','index':0}}
            self.aggregator_cleared_metrics = {'Metadata':aggregator_cleared_meta,'StartTime':self.startTime.strftime("%Y-%m-%d %H:%M:%S")}
        
        @Core.receiver('onsetup')
        def setup(self, sender, **kwargs):
            self._agent_id = config['agentid']
            
        @Core.receiver('onstart')            
        def startup(self, sender, **kwargs):
            
            # Open the JSON file
            self.aggregator_op = open ("aggregator_" + config['agentid'] + "_metrics.json", "w")
            self.controller_op = open ("controller_" + config['agentid'] + "_metrics.json", "w")

            # Initialize subscription function to controllers
            for topic in self.subscriptions['controller']:
                _log.info('Subscribing to ' + topic)
                self.vip.pubsub.subscribe(peer='pubsub',
                                          prefix=topic,
                                          callback=self.on_receive_controller_message)
            
            # Initialize subscription function to GLD meter:
            for topic in self.subscriptions['meter']:
                _log.info('Subscribing to ' + topic)
                self.vip.pubsub.subscribe(peer='pubsub',
                                          prefix=topic,
                                              callback=self.on_receive_GLD_message_fncs)
            
            # Initialize subscription function to fncs_bridge:
            for topic in self.subscriptions['fncs_bridge']:
                _log.info('Subscribing to ' + topic)
                self.vip.pubsub.subscribe(peer='pubsub',
                                          prefix=topic,
                                              callback=self.on_receive_fncs_bridge_message_fncs)
                
            # Initialize subscription function to coordinator:
            for topic in self.subscriptions['coordinator']:
                _log.info('Subscribing to ' + topic)
                self.vip.pubsub.subscribe(peer='pubsub',
                                          prefix=topic,
                                              callback=self.on_receive_coordinator_message)
                
            # Publish the initial market information
            self.market['clearat'] = self.startTime + datetime.timedelta(0,self.market['period'])  
            # Update statistics
            self.update_statistics()
            # Publish market data at the initial time step
            # Create a message for all points.
            all_message = [{'market_id': self.market['market_id'], 
                            'std_dev': self.market['init_stdev'], 
                            'average_price': self.market['init_price'],
                            'clear_price': self.market['init_price'], 
                            'price_cap': self.market['pricecap'], 
                            'period': self.market['period'],
                            'initial_price': self.market['init_price']                            
                            },
                           {'market_id': {'units': 'none', 'tz': 'UTC', 'type': 'integer'},
                            'std_dev': {'units': '$', 'tz': 'UTC', 'type': 'float'}, 
                            'average_price': {'units': '$', 'tz': 'UTC', 'type': 'float'},
                            'clear_price': {'units': '$', 'tz': 'UTC', 'type': 'float'},
                            'price_cap': {'units': '$', 'tz': 'UTC', 'type': 'float'}, 
                            'period': {'units': 'second', 'tz': 'UTC', 'type': 'float'},
                            'initial_price': {'units': '$', 'tz': 'UTC', 'type': 'float'}                          
                            }]
            pub_topic = 'aggregator/' + self.market['name'] + '/all'
            _log.info('Aggregator agent {0} publishes cleared data to controllers with topic: {1}'.format(self.market['name'], pub_topic))
            #Create timestamp
            now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
            headers = {
                headers_mod.DATE: now
            }
            self.vip.pubsub.publish('pubsub', pub_topic, headers, all_message)
            
        # ====================extract float from string ===============================
        def get_num(self,fncs_string):
            return float(''.join(ele for ele in fncs_string if ele.isdigit() or ele == '.'))
        
        # ====================Obtain values from controller ===========================
        def on_receive_controller_message(self, peer, sender, bus, topic, headers, message):
            """Subscribe to controller publications and change the data accordingly 
            """    
#             _log.info("Whole message", topic, message)
#             #The time stamp is in the headers
#             _log.info('Date', headers['Date'])

            # Find the controller name who sends the message
            controller = topic.split("/")[-2]
            # Update controller data 
            val =  message[0]
#             _log.info('Aggregator {0:s} recieves from controller the bids.'.format(self.market['name']))
            propertyKeys = val.keys()          
            # Check if it is rebid. If true, then have to delete the existing bid if any
            if self.market['market_id'] == val['market_id']:
                if val['rebid'] != 0:
                    # Check if the bid from the same bid_id is stored, if so, delete
                    if (val['bid_id'] in self.buyer['bid_id']):
                        index_delete = self.buyer['bid_id'].index(val['bid_id'])
                        print ('  removing list index', index_delete)
                        for ele in self.buyer.keys():
                            del self.buyer[ele][index_delete]
                # Add the new bid:
                self.buyer['name'].append(val['bid_name'])
                self.buyer['price'].append(val['price'])
                self.buyer['quantity'].append(val['quantity'])
                self.buyer['state'].append(val['state'])
                self.buyer['bid_id'].append(val['bid_id'])
            
            if self.market['market_id'] < val['market_id']:
                print('bidding into future markets is not yet supported')
        
        # ====================Obtain values from GLD ===========================
        def on_receive_GLD_message_fncs(self, peer, sender, bus, topic, headers, message):
            """Subscribe to GLD publications and change the data accordingly 
            """    

            val =  message[0]/1000 # Convert unit to kW
#             _log.info('Aggregator {0:s} recieves from GLD the real power {1} kW.'.format(self.market['name'], val))
            self.market['capacity_reference_object']['capacity_reference_property'] = val
            
            # Publish the total loads seen by aggregator to coordinator
            pub_topic = 'aggregator/' + self.market['name'] + '/aggregatorLoad'
#             _log.info('Aggregator agent {0} publishes monitored total loads downstrean to coordinator: {1}'.format(self.market['name'], pub_topic))
            now = datetime.datetime.utcnow().isoformat(' ') + 'Z' #Create timestamp
            headers = {
                headers_mod.DATE: now
            }
            self.vip.pubsub.publish('pubsub', pub_topic, headers, message)
        
        # ====================Obtain values from coordinator ===========================
        def on_receive_coordinator_message(self, peer, sender, bus, topic, headers, message):
            """Subscribe to coordinator publications and change the "fixed price" accordingly 
            """    

            # Update coordinator data 
            val = message[0]
            _log.info('Aggregator {0:s} with market_id {1} recieves from coordinator the cleared information.'.format(self.market['name'], self.market['market_id']))  
                
            if (val['market_id'] == self.market['market_id']):
                
                self.coordinator['market_id'] = val['market_id']
                
                if val['no_bid'] == False:
                    self.market['fixed_price'] = val['fixed_price']
                else:
                    self.market['fixed_price'] = self.market_output['mean']
                                
                # Mark "received" flag as true after receiving fromm coordinator
                self.coordinator['received'] = True
                
            else:
                warnings.warn('Coordinator market id {0} is not the same with the aggregator id {1}'.format(val['market_id'], self.market['market_id']))
        
        # ====================Obtain values from fncs_bridge ===========================
        def on_receive_fncs_bridge_message_fncs(self, peer, sender, bus, topic, headers, message):
            """Subscribe to fncs_bridge publications and change the data accordingly 
            """    

            val =  message[0] # value True
#             _log.info('Aggregator {0:s} recieves from fncs_bridge the simulation ends message {1:s}'.format(self.market['name'], val))
            if (val == 'True'):
                # Dump to JSON fies and close the files
                with open(self.controller_op, 'w') as outfile:
                    json.dumps(self.controller_bids_metrics, outfile)
                with open(self.aggregator_op, 'w') as outfile:
                    json.dumps(self.aggregator_cleared_metrics, outfile)
#                 print (json.dumps(self.controller_bids_metrics), file=self.controller_op)
#                 print (json.dumps(self.aggregator_cleared_metrics), file=self.aggregator_op)
#                 self.aggregator_op.close()
#                 self.controller_op.close()
                # End the agent
                self.core.stop() 
            
        @Core.periodic(1)
        def presync(self):
            ''' This method comes from the presync part of the auction source code in GLD 
            '''    
            # Update controller t1 information
            self.timeSim = datetime.datetime.now()
            
#             if self.timeSim % self.market['period'] == 0:
#                 self.nextClear['from'] = self.nextClear['quantity'] = self.nextClear['price'] = 0
            
            # Formulate and publish buyer curve before market clears, and after recieving bid from all buyers
            if self.timeSim >= self.market['clearat'] - datetime.timedelta(0,self.market['bid_delay']) and self.timeSim <= self.market['clearat'] and self.market['market_id'] == self.market['lastmkt_id']: 
                
                self.buyerCurve()
                
                self.market['market_id'] += 1 # This is the market to be cleared
            
            # Start market clearing process
            if self.timeSim >= self.market['clearat'] and self.coordinator['received'] == True:
                
                self.coordinator['received'] = False
            
                # Clear the market by using the fixed_price sent from coordinator
                self.clear_market() 
                
                # Update lastmkt_id since the market just get cleared
                self.market['lastmkt_id'] = self.market['market_id']
                
                # Display the opening of the next market
                tiemDiff = (self.timeSim + datetime.timedelta(0,self.market['period']) - self.market['clearat']).total_seconds() % self.market['period']
#                 self.market['clearat'] = self.timeSim + datetime.timedelta(0,self.market['period'] - tiemDiff)
                self.market['clearat'] = self.market['clearat'] + datetime.timedelta(0,self.market['period'])
                # self.market['clearat'] = self.timeSim + self.market['period'] - (self.timeSim + self.market['period']) % self.market['period']
            
                # Update to be published values only when market clears
                # if self.market_output['market_id'] != 'none':
                    # self.market_output['market_id'] = self.market['market_id'] # Update the market_id sent to controller      
                    
                # Create a message for all points.
                all_message = [{'market_id': self.market_output['market_id'], 
                                'std_dev': self.market_output['std'], 
                                'average_price': self.market_output['mean'],
                                'clear_price': self.market_output['clear_price'], 
                                'price_cap': self.market_output['pricecap'], 
                                'period': self.market['period'],
                                'initial_price': self.market['init_price']                          
                                },
                               {'market_id': {'units': 'none', 'tz': 'UTC', 'type': 'integer'},
                                'std_dev': {'units': '$', 'tz': 'UTC', 'type': 'float'}, 
                                'average_price': {'units': '$', 'tz': 'UTC', 'type': 'float'},
                                'clear_price': {'units': '$', 'tz': 'UTC', 'type': 'float'},
                                'price_cap': {'units': '$', 'tz': 'UTC', 'type': 'float'}, 
                                'period': {'units': 'second', 'tz': 'UTC', 'type': 'float'},
                                'initial_price': {'units': '$', 'tz': 'UTC', 'type': 'float'}                          
                                }]
                pub_topic = 'aggregator/' + self.market['name'] + '/all'
                _log.info('Aggregator agent {0} publishes cleared data to controllers with market_id {1}, average_price: {2}, clear_price: {3}'.format(self.market['name'], self.market_output['market_id'], self.market_output['mean'], self.market_output['clear_price']))
                #Create timestamp
                now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
                headers = {
                    headers_mod.DATE: now
                }
                self.vip.pubsub.publish('pubsub', pub_topic, headers, all_message)
        
        # ======================== Update statistics for the calculation of std and mean ==============    
        def update_statistics(self):
            sample_need = skipped = 0
            meanVal = stdev = 0.0
            startIdx = stopIdx = idx = 0
            
            # If no statistics
            if self.market['statistic_count'] < 1:
                return
            
            if self.market['new_prices'][0] == 0:
                return
            
            # Caluclate values for each stat mode
            for k in range(0, len(self.stats['interval'])):
                meanVal = 0.0
                sample_need = int (self.stats['interval'][k]/self.market['period'])
                if self.stats['stat_mode'][k] == 'ST_CURR':
                    stopIdx = self.market['price_index']
                elif self.stats['stat_mode'][k] == 'ST_PAST':
                    stopIdx = self.market['price_index'] - 1
                    
                # Calculate start index
                startIdx = (self.market['history_count'] + stopIdx - sample_need) % self.market['history_count']
                for i in range(0, sample_need):
                    idx = (startIdx + i + self.market['history_count']) % self.market['history_count']
                    if self.market['ignore_pricecap'] == 'IP_TRUE' and (self.market['new_prices'][idx] == self.market['pricecap'] or self.market['new_prices'][idx] == -self.market['pricecap']):
                        skipped+= 1
                    elif self.market['ignore_failedmarket'] == 'IFM_TRUE' and self.market['new_market_failures'][idx] == 'CT_FAILURE':
                        skipped+= 1
                    else:
                        meanVal += self.market['new_prices'][idx]
                
                # Calculate mean values:
                if skipped != sample_need:
                    meanVal /= (sample_need - skipped)
                else:
                    meanVal = 0.0
                    warnings.warn('All values in auction statistic calculations were skipped. Setting mean to zero.')
                if self.market['use_future_mean_price'] == 1:
                    meanVal = self.market['future_mean_price']
                if self.stats['stat_type'][k] == 'SY_MEAN':
                    self.stats['value'][k] = meanVal
                elif self.stats['stat_type'][k] == 'SY_STDEV':
                    x = 0.0
                    if (sample_need + (1 if self.stats['stat_mode'][k] == 'ST_PAST' else 0)) > self.market['total_samples']:
                        self.stats['value'][k] = self.market['init_stdev']
                    else:
                        stdev = 0.0
                        for j in range(0, sample_need):
                            idx = (startIdx + j + self.market['history_count']) % self.market['history_count']
                            if self.market['ignore_pricecap'] == 'IP_TRUE' and (self.market['new_prices'][idx] == self.market['pricecap'] or self.market['new_prices'][idx] == self.market['pricecap']):
                                pass # ignore the value
                            if self.market['ignore_pricecap'] == 'IFM_TRUE' and self.market['new_market_failures'][idx] == 'CT_FAILURE':
                                pass # ignore the value
                            else:
                                x = self.market['new_prices'][idx] - meanVal
                                stdev += x*x
                        if skipped != sample_need:
                            stdev /= (sample_need - skipped)
                        else:
                            stdev = 0.0
                        self.stats['value'][k] = math.sqrt(stdev)
                        
                # Give the updated mean snd std values to the market_output        
                if self.market['statistic_mode'] == 1:
                    if self.market['latency'] == 0:
                        if self.stats['stat_type'][k] == 'SY_MEAN':
                            self.market_output['mean'] = self.stats['value'][k]
                        elif self.stats['stat_type'][k] == 'SY_STDEV':
                            self.market_output['std'] = self.stats['value'][k]
        
        # =========================================== Obtain and publish buyer curve ======================================================   
        def buyerCurve(self):
            # Beofore market clears (clear time - delay time), aggregator needs to formulate buyer curve, and send to coordinator
            
            # Curves need to be re-initialized
            curve_buyer = curve()
            # Iterate each buyer to obtain the final buyer curve    
            for i in range (len(self.buyer['name'])):
                curve_buyer.add_to_curve(self.buyer['price'][i], self.buyer['quantity'][i], self.buyer['name'][i], self.buyer['state'][i])
                        
            # "Bid" at the price cap from the unresponsive load (add this last, when we have a summary of the responsive bids)
            # Change the condition to apply to only MD_BUYERS mode, since it is the mode we are using now
            if self.market['capacity_reference_object']['name'] != 'none' and self.market['special_mode'] == 'MD_BUYERS':
                total_unknown = curve_buyer.total - curve_buyer.total_on - curve_buyer.total_off
                if total_unknown > 0.001:
                    warnings.warn('total_unknown is non-zero; some controllers are not providing their states with their bids')
                refload = self.market['capacity_reference_object']['capacity_reference_property']
                unresp = refload - curve_buyer.total_on - total_unknown/2
                print('  Unresponsive load bid: Refload,#buyers,on,off,unresp=', refload, curve_buyer.count, curve_buyer.total_on, curve_buyer.total_off, unresp)
    #            unresp = 2000.0
                # unresp = 30.0
                # print('  MANUAL override', unresp, 'kW unresponsive load bid')

                if unresp < -0.001:
                    warnings.warn('capacity_reference has negative unresponsive load--this is probably due to improper bidding')
                elif unresp > 0.001:
                    self.buyer['name'].append(self.market['capacity_reference_object']['name'])
                    self.buyer['price'].append(float(self.market['pricecap']))
                    self.buyer['quantity'].append(unresp) # buyer bid in cpp codes is negative, here bidder quantity always set positive
                    self.buyer['state'].append('ON')
                    self.buyer['bid_id'].append(self.market['capacity_reference_object']['name'])
                    curve_buyer.add_to_curve(self.market['pricecap'], unresp, self.market['capacity_reference_object']['name'], 'ON')
             
            # Sort buyer curve
            if curve_buyer.count > 0:
                curve_buyer.set_curve_order ('descending')    
                           
                # Print out buyer curve and rearrange self.buyer array
                print ('Buyer Curve at ', self.timeSim.strftime("%Y-%m-%d %H:%M:%S"))
                self.buyer = {'name': [], 'price': [], 'quantity': [], 'state': [], 'bid_id': []}  # initialize the seller and buyer dictionary
                # Stor buyer curve value to controller_bid_metrics
                self.controller_bids_metrics[self.timeSim.strftime("%Y-%m-%d %H:%M:%S")] = {}
                for i in range(curve_buyer.count):
                    print ('  ', i, curve_buyer.bidname[i], curve_buyer.quantity[i], curve_buyer.price[i])
                    self.buyer['price'].append(curve_buyer.price[i])
                    self.buyer['quantity'].append(curve_buyer.quantity[i])
                    self.buyer['name'].append(curve_buyer.bidname[i])
                    # Store bid into JSON metrics
                    self.controller_bids_metrics[self.timeSim.strftime("%Y-%m-%d %H:%M:%S")][curve_buyer.bidname[i]] = [curve_buyer.price[i], curve_buyer.quantity[i]]
                    
            # Publish buyer curve setpoints
            all_message = [{'market_id': self.market['market_id'], 
                'price': self.buyer['price'], 
                'quantity': self.buyer['quantity'],
                'name': self.buyer['name']                          
                },
               {'market_id': {'units': 'none', 'tz': 'UTC', 'type': 'integer'},
                'price': {'units': '$', 'tz': 'UTC', 'type': 'float'}, 
                'quantity': {'units': '', 'tz': 'UTC', 'type': 'list'},
                'name': {'units': '', 'tz': 'UTC', 'type': 'list'}                         
                }]
            pub_topic = 'aggregator/' + self.market['name'] + '/biddings/all'
            _log.info('aggregator agent {0} with market_id {1} publishes updated biddings to coordinator agent'.format(self.market['name'], self.market['market_id']))
            # Create timestamp
            now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
            headers = {
                headers_mod.DATE: now
            }
            self.vip.pubsub.publish('pubsub', pub_topic, headers, all_message)
       
        # =========================================== Clear market ======================================================            
        def clear_market(self):
            
            bid_offset = 0.0001
            cap_ref_unrep = 0.0

            # These need to be re-initialized
            unresponsive_sell = unresponsive_buy =  responsive_sell =  responsive_buy = 0
            
            # Check special_mode and sort buyers and sellers curves
            single_quantity = single_price = 0.0
            
            if self.market['special_mode'] == 'MD_BUYERS':

                # Rearranged fix price or quantity 
                if self.market['fixed_price'] * self.market['fixed_quantity'] != 0:
                    warnings.warn('fixed_price and fixed_quantity are set in the same single auction market ~ only fixed_price will be used')
                
                if self.market['fixed_quantity'] > 0.0:
                    for i in range(len(self.buyer['name'])):
                        single_price = self.buyer['price'][i]
                        single_quantity += self.buyer['quantity'][i]
                        if single_quantity >= self.market['fixed_quantity']: 
                            break
                    if single_quantity > self.market['fixed_quantity']: 
                            single_quantity = self.market['fixed_quantity']
                            clearing_type = 'CT_BUYER'
                    elif single_quantity == self.market['fixed_quantity']:
                            clearing_type = 'CT_EXACT'
                    else:
                        clearing_type = 'CT_FAILURE'
                        single_quantity = 0.0
                        single_price = 0 if len(self.buyer['name']) == 0 else self.buyer['price'][0] + bid_offset
                
                elif self.market['fixed_quantity'] < 0.0:
                    warnings.warn('fixed_quantity is negative')
               
                else:
                    single_price = self.market['fixed_price']
                    for i in range(len(self.buyer['name'])):
                        if self.buyer['price'][i] >= self.market['fixed_price']:
                            single_quantity += self.buyer['quantity'][i]
                        else: break
                    if single_quantity > 0.0: 
                        clearing_type = 'CT_EXACT'
                    else: 
                        clearing_type = 'CT_NULL'
                        
                self.nextClear['price'] = single_price
                self.nextClear['quantity'] = single_quantity  
            
            else:
                raise ValueError('Currently only the MD_BUYERS mode aggregator is defined')

            # # Calculate clearing price and quantity
            # if curve_buyer.count > 0:
                # curve_buyer.set_curve_order ('descending')
            # if curve_seller.count > 0:
                # curve_seller.set_curve_order ('ascending')

            # If the market mode is MD_SELLERS or MD_BUYERS:
            if self.market['special_mode'] == 'MD_SELLERS' or self.market['special_mode'] == 'MD_BUYERS':
                # Update market output information
                self.market_output['clear_price'] = self.nextClear['price']
                self.market_output['pricecap'] = self.market['pricecap']
                self.market_output['market_id'] = self.market['market_id']
            
            else:
                raise ValueError('Currently only the MD_BUYERS mode aggregator is defined')
                           
            # Calculation of the marginal 
            marginal_total = marginal_quantity = marginal_frac = 0.0
            if clearing_type == 'CT_BUYER':
                marginal_subtotal = 0
                i = 0
                for i in range(len(self.buyer['name'])):
                    if self.buyer['price'][i] > self.nextClear['price']:
                        marginal_subtotal = marginal_subtotal + self.buyer['quantity'][i]
                    else:
                        break
                marginal_quantity =  self.nextClear['quantity'] - marginal_subtotal
                for j in range(i, len(self.buyer['name'])):
                    if self.buyer['price'][i] == self.nextClear['price']:
                        marginal_total += self.buyer['quantity'][i]
                    else:
                        break
                if marginal_total > 0.0:
                    marginal_frac = float(marginal_quantity) / marginal_total
           
            elif clearing_type == 'CT_SELLER':
                marginal_subtotal = 0
                i = 0
                for i in range(0, self.curve_seller.count):
                    if self.curve_seller.price[i] > self.nextClear['price']:
                        marginal_subtotal = marginal_subtotal + self.curve_seller.quantity[i]
                    else:
                        break
                marginal_quantity =  self.nextClear['quantity'] - marginal_subtotal
                for j in range(i, self.curve_seller.count):
                    if self.curve_seller.price[i] == self.nextClear['price']:
                        marginal_total += self.curve_seller.quantity[i]
                    else:
                        break
                if marginal_total > 0.0:
                    marginal_frac = float(marginal_quantity) / marginal_total 
            
            else:
                marginal_quantity = 0.0
                marginal_frac = 0.0
            

#             print(self.timeSim.strftime("%Y-%m-%d %H:%M:%S"),'(Type,Price,MargQ,MargT,MargF)',clearing_type, self.nextClear['price'], marginal_quantity, marginal_total, marginal_frac)

            # Store cleared market information into JSON metrics
            self.aggregator_cleared_metrics[self.timeSim.strftime("%Y-%m-%d %H:%M:%S")] = self.nextClear['price']
                    
            # Update new_price and price_index, for the calculation of sdv and mean from update_statistics later
            if self.market['history_count'] > 0:
                # If the market clearing times equal to the described statistic interval, update it from 0
                if self.market['price_index'] == self.market['history_count']:
                    self.market['price_index'] = 0
                # Put the newly cleared price into the new_prices array
                self.market['new_prices'][self.market['price_index']] = self.nextClear['price']
                self.market['new_market_failures'][self.market['price_index']] = self.market['current_frame']['clearing_type']
                # Update price_index
                self.market['price_index'] += 1
            
            # Limit price within the pricecap
            if self.nextClear['price'] < -self.market['pricecap']:
                self.nextClear['price'] = -self.market['pricecap']
            
            elif self.nextClear['price'] > self.market['pricecap']:
                self.nextClear['price'] = self.market['pricecap']
            
            # Update cleared_frame data
            self.market['cleared_frame']['market_id'] = self.market['market_id']
            self.market['cleared_frame']['start_time'] = self.timeSim + datetime.timedelta(0,self.market['latency'])
            self.market['cleared_frame']['end_time'] = self.timeSim + datetime.timedelta(0,self.market['latency']+ self.market['period'])
            self.market['cleared_frame']['clearing_price'] = self.nextClear['price']
            self.market['cleared_frame']['clearing_quantity'] = self.nextClear['quantity']
            self.market['cleared_frame']['clearing_type'] = clearing_type
            self.market['cleared_frame']['marginal_quantity'] = marginal_quantity
            self.market['cleared_frame']['total_marginal_quantity'] = marginal_total
            self.market['cleared_frame']['buyer_total_quantity'] = len(self.buyer['name'])
            self.market['cleared_frame']['seller_total_quantity'] = len(self.seller['name'])
            if len(self.seller['name']) > 0:
                self.market['cleared_frame']['seller_min_price'] = min(self.buyer['price'])
            self.market['cleared_frame']['marginal_frac'] = marginal_frac
            self.market['cleared_frame']['buyer_total_unrep'] = unresponsive_buy
            self.market['cleared_frame']['cap_ref_unrep'] = cap_ref_unrep
            
            # Update current_frame
            if self.market['latency'] > 0:
                
                self.pop_market_frame()
                self.update_statistics()
                self.push_market_frame()
                
            else:
                
                self.market['past_frame'] = deepcopy(self.market['current_frame'])
                # Copy new data in
                self.market['current_frame']= deepcopy(self.market['cleared_frame'])
                # Update market total_samples numbers
                self.market['total_samples'] += 1
                # Update statistics for the calculation of std and mean
                self.update_statistics()
            
            # End of the clear_market def            
            # self.curve_seller = None
            # self.curve_buyer = None
            
            # initialize the seller and buyer dictionary
            self.buyer = {'name': [], 'price': [], 'quantity': [], 'state': [], 'bid_id': []}
            self.seller = {'name': [], 'price': [], 'quantity': [], 'state': [], 'bid_id': []} 
        
         # =========================================== Pop market ======================================================
    # Fill in the exposed current market values with those within the
        def pop_market_frame(self):
            
            # Check if market framedata queue has any data
            if self.market['latency_front'] == self.market['latency_back']:
                print ('market latency queue has no data')
                return
            
            # Obtain the current market frame used
            frame = self.market['framedata'][self.market['latency_front']]
            
            # Check if the starting the frame
            if self.timeSim < frame['start_time']:
                print ('market latency queue data is not yet applicable')
                return 
            
            # Copy current frame data to past_frame
            self.market['past_frame'] = deepcopy(self.market['current_frame'])
            
            # Copy new data to the current frame
            self.market['current_frame'] = deepcopy(frame)
            
            # Copy statistics
            # Give the updated mean snd std values to the market_output        
            if self.market['statistic_mode'] == 1:
                for k in range(0, len(self.stats['stat_type'])):
                    if self.stats['stat_type'][k] == 'SY_MEAN':
                        self.market_output['mean'] = frame['statistics'][k]
                    elif self.stats['stat_type'][k] == 'SY_STDEV':
                        self.market_output['std'] = frame['statistics'][k]
    
            # Having used latency_front index, push the index forward
            self.market['latency_front'] = (self.market['latency_front'] + 1) / self.market['latency_count']    
        
        # =========================================== push market ======================================================
        # Take the current market values and enqueue them on the end of the latency frame queue
        def push_market_frame(self):
        
            if (self.market['latency_back'] + 1) % self.market['latency_count'] == self.market['latency_front']:
                raise ValueError('market latency queue is overwriting as-yet unused data, so is not long enough or is not consuming data')
            
            # Copy cleared frame data into the current market frame used
            self.market['framedata'][self.market['latency_back']] = deepcopy(self.market['cleared_frame'])
            self.market['framedata'][self.market['latency_back']]['statistics'] = deepcopy(self.stats['value'])
            
            # Update latency_back index:
            self.market['latency_back'] = (self.market['latency_back'] + 1) % self.market['latency_count']  
            
            if self.market['latency'] > 0:
                self.market['total_samples'] += 1
        
                      
    Agent.__name__ = config['agentid']
    return aggregatorAgent(**kwargs)        
                
def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(aggregator_agent)
    except Exception as e:
        print e
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
                         