import datetime
import logging
import sys
import uuid
import math
import warnings

from volttron.platform.vip.agent import Agent, Core, PubSub, compat
from volttron.platform.agent import utils
from volttron.platform.messaging import topics, headers as headers_mod

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '0.1'

def controller_agent(config_path, **kwargs):
    
    # Obtain the agent subscription and initial values from config file
    config = utils.load_config(config_path)
    houses = config['houses']
    aggregatorDetail = config['aggregator']
    aggregatorInfo = config['aggregator_information']
    fncs_bridgeInfo = config['fncs_bridge']
#     agentSubscription = config['subscriptions']
#     agentInitialVal = config['initial_value']
    
    class controllerAgent(Agent):
        '''This agent is the bottom level controller that bids the price and quantity to the upper level agent,
        recives the clearing price, and adjusts the house set point accordingly
        '''
        def __init__(self, **kwargs):
            
            super(controllerAgent, self).__init__(**kwargs)
            
            self.startTime = datetime.datetime.now()
            _log.info('Simulation starts from: {0} in controller agent {1}.'.format(str(self.startTime), config['agentid']))
            
            houseGroupId = config['agentid'].replace('controller', '')
            
            # Initialize the instance variables
            self.aggregator = {'name': 'none', 'market_id': 0, 'average_price': -1, 'std_dev': -1, 'clear_price': -1, \
                  'initial_price': -1, 'price_cap':9999.0, 'period': -1}
                              
            # market information for aggregator agent - Market registration information
            # self.aggregator['name'] = self.controller[houseName]['aggregatorName']
            self.aggregator['market_id'] = aggregatorInfo['market_id']
            self.aggregator['market_unit'] = aggregatorInfo['aggregator_unit']
            self.aggregator['initial_price'] = aggregatorInfo['initial_price']
            self.aggregator['average_price'] = aggregatorInfo['average_price']
            self.aggregator['std_dev'] = aggregatorInfo['std_dev']
            self.aggregator['clear_price'] = aggregatorInfo['clear_price']
            self.aggregator['price_cap'] = aggregatorInfo['price_cap']
            self.aggregator['period'] = aggregatorInfo['period']
            
            #
            self.house = {}
            self.controller = {}
            self.controller_bid = {}
            self.bidded = {}
            self.subscriptions = {}
                
            # Initialize the variables - loop through each house controlled by this controller
            for oneHouse in houses:
                
                houseName = oneHouse.keys()
                if len(houseName) != 1:
                    raise ValueError('For each house, more than one house keys are given')
                else:
                    houseName = houseName[0]
                houseInfo = oneHouse[houseName]
            
                agentInitialVal = houseInfo['initial_value']
                agentSubscription = houseInfo['subscriptions']    
                
                self.house[houseName] = {'target': 'air_temperature', 'setpoint0':-1, 'lastsetpoint0': 0, 'controlled_load_all': 1, 'controlled_load_curr': 1, \
                 'uncontrolled_load': 1, 'deadband': 0, 'currTemp': -1, 'powerstate': 'UNKNOWN', 'last_pState': 'UNKNOWN', 
                 'heating_demand': 0, 'cooling_demand': 0, 'aux_state': 0, 'heat_state': 0, 'cool_state': 0, 
                 'thermostat_state': 'UNKNOWN', 
                 'heating_setpoint0': -1, 'cooling_setpoint0': -1, 
                 're_override': 'NORMAL'
                 }
                
                self.controller[houseName] = {'name': 'none','marketName': 'none', 'houseName': 'none', 'simple_mode': 'none', 'setpoint': 'none', 'lastbid_id': -1, 'lastmkt_id': -1, 'bid_id': 'none', \
                      'slider_setting': -0.001, 'period': -1, 'ramp_low': 0, 'ramp_high': 0, 'range_low': 0, \
                      'range_high': 0, 'dir': 0, 'direction': 0, 'use_predictive_bidding': 0, 'deadband': 0, 'last_p': 0, \
                      'last_q': 0, 'setpoint0': -1, 'minT': 0, 'maxT': 0, 'bid_delay': 60, 'next_run': 0, 't1': 0, 't2': 0, 
                      'use_override': 'OFF', 'control_mode': 'CN_RAMP', 'resolve_mode': 'DEADBAND', 
                      'slider_setting': -0.001, 'slider_setting_heat': -0.001, 'slider_setting_cool': -0.001, 'sliding_time_delay': -1,
                      'heat_range_high': 3, 'heat_range_low': -5, 'heat_ramp_high': 0, 'heating_ramp_low': 0,
                      'cool_range_high': 5, 'cool_range_low': -3, 'cooling_ramp_high': 0, 'cooling_ramp_low': 0,
                      'heating_setpoint0': -1, 'cooling_setpoint0': -1, 'heating_demand': 0, 'cooling_demand': 0,
                      'sliding_time_delay': -1, 
                      'thermostat_mode': 'INVALID',  'last_mode': 'INVALID', 'previous_mode': 'INVALID',
                      'time_off': sys.maxsize
                      }
                
                self.controller_bid[houseName] = {'market_id': -1, 'bid_id': 'none', 'bid_price': 0.0, 'bid_quantity': 0, 'bid_accepted': 1, \
                                       'state': 'UNKNOWN', 'rebid': 0}
                
                # Read and assign initial values from agentInitialVal
                # controller information
                self.controller[houseName]['name'] = houseName #config['agentid']
                self.controller[houseName]['control_mode'] = agentInitialVal['controller_information']['control_mode']
                self.controller[houseName]['aggregatorName'] = agentInitialVal['controller_information']['aggregatorName']
                self.controller[houseName]['houseName'] = agentInitialVal['controller_information']['houseName']
                self.controller[houseName]['bid_id'] = agentInitialVal['controller_information']['bid_id']
                self.controller[houseName]['period'] = agentInitialVal['controller_information']['period']
                self.controller[houseName]['ramp_low'] = agentInitialVal['controller_information']['ramp_low']
                self.controller[houseName]['ramp_high'] = agentInitialVal['controller_information']['ramp_high']
                self.controller[houseName]['range_low'] = agentInitialVal['controller_information']['range_low']
                self.controller[houseName]['range_high'] = agentInitialVal['controller_information']['range_high']
                self.controller[houseName]['setpoint0'] = agentInitialVal['controller_information']['base_setpoint']
                self.controller[houseName]['bid_delay'] = agentInitialVal['controller_information']['bid_delay']
                self.controller[houseName]['use_predictive_bidding'] = agentInitialVal['controller_information']['use_predictive_bidding']
                self.controller[houseName]['use_override'] = agentInitialVal['controller_information']['use_override']
                self.controller[houseName]['last_setpoint'] = self.controller[houseName]['setpoint0']
                 
                 
                # house information  - values will be given after the first time step, thereforely here set as default zero values
                self.house[houseName]['currTemp'] = 0
                self.house[houseName]['powerstate'] = "ON"
                self.house[houseName]['controlled_load_all'] = 0 
                self.house[houseName]['target'] = "air_temperature"
                self.house[houseName]['deadband'] = 2 
    #             self.house['setpoint0'] = 0
    #             self.house['lastsetpoint0'] = self.house['setpoint0']
                
                ## Rearrange object based on given initial value
                # Assign default values if it is simple mode:
                if self.controller[houseName]['simple_mode'] == 'house_heat':
                    self.controller[houseName]['setpoint'] = 'heating_setpoint'
                    self.controller[houseName]['ramp_low'] = self.controller[houseName]['ramp_high'] = -2
                    self.controller[houseName]['range_low'] = -5
                    self.controller[houseName]['range_high'] = 0
                    self.controller[houseName]['dir'] = -1
                elif self.controller[houseName]['simple_mode'] == 'house_cool':
                    self.controller[houseName]['setpoint'] = 'cooling_setpoint'
                    self.controller[houseName]['ramp_low'] = self.controller[houseName]['ramp_high'] = 2
                    self.controller[houseName]['range_low'] = 0
                    self.controller[houseName]['range_high'] = 5
                    self.controller[houseName]['dir'] = 1
                elif self.controller[houseName]['simple_mode'] == 'house_preheat':
                    self.controller[houseName]['setpoint'] = 'heating_setpoint'
                    self.controller[houseName]['ramp_low'] = self.controller[houseName]['ramp_high'] = -2
                    self.controller[houseName]['range_low'] = -5
                    self.controller[houseName]['range_high'] = 3
                    self.controller[houseName]['dir'] = -1
                elif self.controller[houseName]['simple_mode'] == 'house_precool':
                    self.controller[houseName]['setpoint'] = 'cooling_setpoint'
                    self.controller[houseName]['ramp_low'] = self.controller[houseName]['ramp_high'] = 2
                    self.controller[houseName]['range_low'] = -3
                    self.controller[houseName]['range_high'] = 5
                    self.controller[houseName]['dir'] = 1
                elif self.controller[houseName]['simple_mode'] == 'waterheater':
                    self.controller[houseName]['setpoint'] = 'tank_setpoint'
                    self.controller[houseName]['ramp_low'] = self.controller[houseName]['ramp_high'] = -2
                    self.controller[houseName]['range_low'] = 0
                    self.controller[houseName]['range_high'] = 10
                elif self.controller[houseName]['simple_mode'] == 'double_ramp':
                    self.controller[houseName]['heating_setpoint'] = 'heating_setpoint'
                    self.controller[houseName]['cooling_setpoint'] = 'cooling_setpoint'
                    self.controller[houseName]['heat_ramp_low'] = self.controller[houseName]['heat_ramp_high'] = -2
                    self.controller[houseName]['heat_range_low'] = -1
                    self.controller[houseName]['heat_range_high'] = 5
                    self.controller[houseName]['cool_ramp_low'] = self.controller[houseName]['cool_ramp_high'] = 2
                    self.controller[houseName]['cool_range_low'] = 5
                    self.controller[houseName]['cool_range_high'] = 5
                    
                # Update controller bidding period:
                if self.controller[houseName]['period'] == 0.0:
                    self.controller[houseName]['period'] = 60
                
                # If the controller time interval is smaller than the aggregator time interval
                if self.aggregator['period'] > self.controller[houseName]['period']:
                    if self.aggregator['period'] % self.controller[houseName]['period'] != 0:
                        warnings.warn('The supply bid and demand bids do not coincide, with the given aggregator time interval\
                         %d s and controller time interval %d s' % (self.aggregator['period'], self.controller[houseName]['period']))   
                    elif self.aggregator['period'] < self.controller[houseName]['period']:
                        # It is not allowed to have larger controller time interval than the market time interval
                        warnings.warn('The controller time interval %d s is larger than the aggregator time interval %d s' \
                                      % (self.controller[houseName]['period'], self.aggregator['period']))
                
                # Update bid delay:
                if self.controller[houseName]['bid_delay'] < 0:
                    self.controller[houseName]['bid_delay'] = -self.controller[houseName]['bid_delay']
                    
                if self.controller[houseName]['bid_delay'] > self.controller[houseName]['period']:
                    warnings.warn('Bid delay is greater than the controller period. Resetting bid delay to 0.')
                    self.controller[houseName]['bid_delay'] = 0
                
                # Check for abnormal input given
                if self.controller[houseName]['use_predictive_bidding'] == 1 and self.controller[houseName]['deadband'] == 0:
                    warnings.warn('Controller deadband property not specified')
                    
                # Calculate dir:
                if self.controller[houseName]['dir'] == 0:
                    high_val = self.controller[houseName]['ramp_high'] * self.controller[houseName]['range_high']
                    low_val = self.controller[houseName]['ramp_low'] * self.controller[houseName]['range_low']
                    if high_val > low_val:
                        self.controller[houseName]['dir'] = 1
                    elif high_val < low_val:
                        self.controller[houseName]['dir'] = -1
                    elif high_val == low_val and (abs(self.controller[houseName]['ramp_high']) > 0.001 or abs(self.controller[houseName]['ramp_low']) > 0.001):
                        self.controller[houseName]['dir'] = 0
                        if abs(self.controller[houseName]['ramp_high']) > 0:
                            self.controller[houseName]['direction'] = 1
                        else:
                            self.controller[houseName]['direction'] = -1
                    if self.controller[houseName]['ramp_low'] * self.controller[houseName]['ramp_high'] < 0:
                        warnings.warn('controller price curve is not injective and may behave strangely')
                
                # Check double_ramp controller mode:
                if self.controller[houseName]['sliding_time_delay'] < 0:
                    self.controller[houseName]['sliding_time_delay'] = 21600 # default sliding_time_delay of 6 hours
                else:
                    self.controller[houseName]['sliding_time_delay'] = int(self.controller[houseName]['sliding_time_delay'])
                
                # use_override
                if self.controller[houseName]['use_override'] == 'ON' and self.controller[houseName]['bid_delay'] <= 0:
                    self.controller[houseName]['bid_delay'] = 1
                  
                # Check slider_setting values
                if self.controller[houseName]['control_mode'] == 'CN_RAMP':
                    if self.controller[houseName]['slider_setting'] < -0.001:
                        warnings.warn('slider_setting is negative, reseting to 0.0')
                        self.controller[houseName]['slider_setting'] = 0.0
                    elif self.controller[houseName]['slider_setting'] > 1.0:
                        warnings.warn('slider_setting is greater than 1.0, reseting to 1.0')
                        self.controller[houseName]['slider_setting'] = 1.0
                        
                    # Obtain minnn and max values - presync part in GLD
                    if self.controller[houseName]['slider_setting'] == -0.001:
                        minT = self.controller[houseName]['setpoint0'] + self.controller[houseName]['range_low']
                        maxT = self.controller[houseName]['setpoint0'] + self.controller[houseName]['range_high']
                        
                    elif self.controller[houseName]['slider_setting'] > 0:
                        minT = self.controller[houseName]['setpoint0'] + self.controller[houseName]['range_low'] * self.controller[houseName]['slider_setting']
                        maxT = self.controller[houseName]['setpoint0'] + self.controller[houseName]['range_high'] * self.controller[houseName]['slider_setting']
                        if self.controller[houseName]['range_low'] != 0:
                            self.controller[houseName]['ramp_low'] = 2 + (1 - self.controller[houseName]['slider_setting'])
                        else:
                            self.controller[houseName]['ramp_low'] = 0
                        if self.controller[houseName]['range_high'] != 0:
                            self.controller[houseName]['ramp_high'] = 2 + (1 - self.controller[houseName]['slider_setting'])
                        else:
                            self.controller[houseName]['ramp_high'] = 0
                            
                    else:
                        minT = maxT = self.controller[houseName]['setpoint0']
                    
                    # Update controller parameters
                    self.controller[houseName]['minT'] = minT;
                    self.controller[houseName]['maxT'] = maxT;
                    
                else:
                    raise ValueError('Currently only the ramp mode controller is defined')
                
                # Intialize controller next_run time as the starting time
                self.controller[houseName]['next_run'] = self.startTime
                
                # Flag indicating whether controller has submitted the bid in this market period, withoout changes of house setpoints or power state
                self.bidded[houseName] = False
                
                # Intialize the controller last time price and quantity 
                self.controller[houseName]['last_p'] = self.aggregator['initial_price']
                self.controller[houseName]['last_q'] = 0
                
                ## Read and define subscription topics from agentSubscription     
                self.subscriptions[houseName] = []   
                # Check agentSubscription
                house = agentSubscription['house']
                if len(house) != 1:
                    raise ValueError('The controller is defined to control more/less than one house, which is not correct')
                 # subscription from house
                for key, val in house[0].items():
                    if self.controller[houseName]['houseName'] != key:
                        raise ValueError('The house name written into subscriptions is not the same as in initial_value')
                    self.subscriptions[houseName] = []
                    for key2, val2 in val.items():
                        topic = 'fncs/output/devices/fncs_Test/' + key + '/' + key2
                        self.subscriptions[houseName].append(topic)
                        
            # subscription from aggregator agent
            aggregator = aggregatorDetail
            if len(aggregator) != 1:
                raise ValueError('The controller is defined to be controlled by more/less than one aggregator agent, which is not correct')
            for key, val in aggregator[0].items():
                if self.controller[houseName]['aggregatorName'] != key:
                    raise ValueError('The aggregator name written into subscriptions is not the same as in initial_value')
                self.subscriptions['aggregator'] = ''
                topic = 'aggregator/' + key + '/all'
                self.subscriptions['aggregator'] = topic
                    
            # subscription from fncs_bridge
            self.subscriptions['fncs_bridge'] = []
            fncs_bridge = fncs_bridgeInfo[0]
            for key, val in fncs_bridge.items():
                topic = key + '/simulation_end'
                self.subscriptions['fncs_bridge'].append(topic)
            
        @Core.receiver('onsetup')
        def setup(self, sender, **kwargs):
            self._agent_id = config['agentid']
        
        
        @Core.receiver('onstart')            
        def startup(self, sender, **kwargs):
            
            # Initialize subscription function to change setpoints
            for oneHouse in houses:
                houseName = oneHouse.keys()
                if len(houseName) != 1:
                    raise ValueError('For each house, more than one house keys are given')
                else:
                    houseName = houseName[0]
                # Assign to subscription topics
                for subscription_topic in self.subscriptions[houseName]:
                    self.vip.pubsub.subscribe(peer='pubsub',
                                              prefix=subscription_topic,
                                                      callback=self.on_receive_house_message_fncs)
                    
            # Initialize subscription function for aggregator
            subscription_topic = self.subscriptions['aggregator']
            self.vip.pubsub.subscribe(peer='pubsub',
                                      prefix=subscription_topic,
                                          callback=self.on_receive_aggregator_message)
                        
            # Initialize subscription function to fncs_bridge:
            for topic in self.subscriptions['fncs_bridge']:
#                 _log.info('Subscribing to ' + topic)
                self.vip.pubsub.subscribe(peer='pubsub',
                                          prefix=topic,
                                              callback=self.on_receive_fncs_bridge_message_fncs)
            
            
        # ====================extract float from string ===============================
        def get_num(self,fncs_string):
            return float(''.join(ele for ele in fncs_string if ele.isdigit() or ele == '.'))

        # ====================Obtain values from house ===========================
        def on_receive_house_message_fncs(self, peer, sender, bus, topic, headers, message):
            """Subscribe to house publications and change the data accordingly 
            """    
#             _log.info("Whole message", topic, message)
#             #The time stamp is in the headers
#             _log.info('Date', headers['Date'])
            # Find the object name who sends the message
            device = topic.split("/")[-2]
            # Find the property sent
            topicProperty = topic.split("/")[-1]
            # Update controller data for house
            val =  message[0]
            if "air_temperature" == topicProperty:
                self.house[device]['currTemp'] = val
#                 _log.info('Controller {0:s} recieves from house {2:s} the current temperature {1:f}.'.format(config['agentid'], val, device))
            if "power_state" == topicProperty:
                self.house[device]['powerstate'] = val
#                 _log.info('Controller {0:s} recieves from house {2:s} the power state {1:s}.'.format(config['agentid'], val, device))
            if "hvac_load" == topicProperty:
                self.house[device]['controlled_load_all'] = val
#                 _log.info('Controller {0:s} recieves from house {2:s} the hvac load amount {1:f}.'.format(config['agentid'], val, device))
            
        # ====================Obtain values from aggregator ===========================
        def on_receive_aggregator_message(self, peer, sender, bus, topic, headers, message):
            """Subscribe to aggregator publications and change the data accordingly 
            """                 
            # Find the aggregator name who sends the message
            aggregatorName = topic.split("/")[-2]
            # Update controller data 
            val = message[0]
#             _log.info('At time {1:s}, controller {0:s} recieves from aggregator the cleared data.'.format(self.controller['name']), self.timeSim.strftime("%Y-%m-%d %H:%M:%S"))      
            self.aggregator['market_id'] = val['market_id']
            self.aggregator['std_dev'] = val['std_dev']
            self.aggregator['average_price'] = val['average_price']
            self.aggregator['clear_price']= val['clear_price']
            self.aggregator['price_cap'] = val['price_cap']
            self.aggregator['initial_price'] = val['initial_price']
        
        # ====================Obtain values from fncs_bridge ===========================
        def on_receive_fncs_bridge_message_fncs(self, peer, sender, bus, topic, headers, message):
            """Subscribe to fncs_bridge publications and change the data accordingly 
            """    

            val =  message[0] # value True
#             _log.info('Aggregator {0:s} recieves from fncs_bridge the simulation ends message {1:s}'.format(self.market['name'], val))
            if (val == 'True'):
                # Dump to JSON fies and close the files
#                 print (json.dumps(self.controller_bids_metrics), file=controller_op)
#                 print (json.dumps(self.aggregator_cleared_metrics), file=aggregator_op)
#                 aggregator_op.close()
#                 controller_op.close()
                # End the agent
                self.core.stop() 
            
        @Core.periodic(1)
        def controller_implementation(self):
            ''' This method comes from the sync and poostsync part of the controller source code in GLD 
            '''    
            self.controller_sync()
            self.controller_postsync()
        
        # ====================Sync content =========================== 
        def controller_sync(self):
            ''' This method comes from the sync and poostsync part of the controller source code in GLD 
            '''          
            for oneHouse in houses:
                
                houseName = oneHouse.keys()
                if len(houseName) != 1:
                    raise ValueError('For each house, more than one house keys are given')
                else:
                    houseName = houseName[0]
                    
                # Update controller t1 information
                self.controller[houseName]['t1'] = datetime.datetime.now()
                
                # Inputs from market object:
                marketId = self.aggregator['market_id']
                clear_price = self.aggregator['clear_price']
                avgP = self.aggregator['average_price']
                stdP = self.aggregator['std_dev']
                
                # Inputs from controller:
                ramp_low = self.controller[houseName]['ramp_low']
                ramp_high = self.controller[houseName]['ramp_high']
                range_low = self.controller[houseName]['range_low']
                range_high = self.controller[houseName]['range_high']
                lastmkt_id = self.controller[houseName]['lastmkt_id']
                deadband = self.controller[houseName]['deadband']
                setpoint0 = self.controller[houseName]['setpoint0']
                last_setpoint = self.controller[houseName]['last_setpoint']
                minT = self.controller[houseName]['minT']
                maxT = self.controller[houseName]['maxT']
                bid_delay = self.controller[houseName]['bid_delay']
                direction = self.controller[houseName]['direction']
                
                # Inputs from house object:
                demand = self.house[houseName]['controlled_load_all']
                monitor = self.house[houseName]['currTemp']
                powerstate = self.house[houseName]['powerstate']
        
        #        print ("  sync:", demand, powerstate, monitor, last_setpoint, deadband, direction, clear_price, avgP, stdP)
                
                # Check t1 to determine if the sync part is needed to be processed or not
                if self.controller[houseName]['t1'] == self.controller[houseName]['next_run'] and marketId == lastmkt_id :
                    return
                
                if  self.controller[houseName]['t1'] < self.controller[houseName]['next_run'] and marketId == lastmkt_id :
                    if self.controller[houseName]['t1'] <= self.controller[houseName]['next_run'] - datetime.timedelta(0,bid_delay):
                        if self.controller[houseName]['use_predictive_bidding'] == 1 and ((self.controller[houseName]['control_mode'] == 'CN_RAMP' and setpoint0 != last_setpoint)):
                            # Base set point setpoint0 is changed, and therefore sync is needed:
                            pass
                        elif self.house[houseName]['last_pState'] != powerstate:
                            # house power state is changed, therefore sync is needed
                            pass
                        elif self.controller[houseName]['use_override'] == 'ON' and self.controller[houseName]['t1'] >= self.controller[houseName]['next_run']- datetime.timedelta(0,bid_delay) and self.bidded[houseName] == False :
                            # At the exact time that controller is operating, therefore sync is needed:
                            self.bidded[houseName] = True # set it as true so that in the same controller period, it will not bid without the changes of house setpoint/power state
                            pass
                        else:
                            return
                    else:
                        return 
                
                # If market get updated, then update the set point                
                deadband_shift = 0
                # Set deadband shift if user predictive bidding is true
                if self.controller[houseName]['use_predictive_bidding'] == 1:
                    deadband_shift = 0.5 * deadband
                
                #  controller update house setpoint if market clears
                if self.controller[houseName]['control_mode'] == 'CN_RAMP':
                     # If market clears, update the setpoints based on cleared market price;
                     # Or, at the beginning of the simlation, update house setpoint based on controller settings (lastmkt_id == -1 at the begining, therefore will go through here)
                    if marketId != lastmkt_id: 
                        
                        # Update controller last market id and bid id
                        self.controller[houseName]['lastmkt_id'] = marketId
                        self.controller[houseName]['lastbid_id'] = -1
                        self.controller_bid[houseName]['rebid'] = 0 
                        
                        # Calculate shift direction
                        shift_direction = 0
                        if self.controller[houseName]['use_predictive_bidding'] == 1:
                            if (self.controller[houseName]['dir'] > 0 and clear_price < self.controller[houseName]['last_p']) or (self.controller[houseName]['dir'] < 0 and clear_price > self.controller[houseName]['last_p']):
                                shift_direction = -1
                            elif (self.controller[houseName]['dir'] > 0 and clear_price >= self.controller[houseName]['last_p']) or (self.controller[houseName]['dir'] < 0 and clear_price <= self.controller[houseName]['last_p']):
                                shift_direction = 1
                            else:
                                shift_direction = 0
                                
                        # Calculate updated set_temp
                        if abs(stdP) < 0.0001:
                            set_temp = setpoint0
                        elif clear_price < avgP and range_low != 0:
                            set_temp = setpoint0 + (clear_price - avgP) * abs(range_low) / (ramp_low * stdP) + deadband_shift*shift_direction
                        elif clear_price > avgP and range_high != 0:
                            set_temp = setpoint0 + (clear_price - avgP) * abs(range_high) / (ramp_high * stdP) + deadband_shift*shift_direction
                        else:
                            set_temp = setpoint0 + deadband_shift*shift_direction
                        
                        # override
        #                 if self.controller[houseName]['use_override'] == 'ON' and self.house[houseName]['re_override'] != 'none':
        #                     if clear_price <= self.controller[houseName]['last_p']:
        #                         self.fncs_publish['controller'][self.controller[houseName]['name']]['override_prop'] = 'ON'
        #                     else:
        #                         self.fncs_publish['controller'][self.controller[houseName]['name']]['override_prop'] = 'OFF'
                        
                        # Check if set_temp is out of limit
                        if set_temp > maxT:
                            set_temp = maxT
                        elif set_temp < minT:
                            set_temp = minT
                            
                        # Update house set point
    #                     if self.controller[houseName]['next_run'] != self.startTime: # At starting time of the simulation, setpoints also need to be updated

                        # Publish the changed setpoints:
                        pub_topic = 'fncs/input' + houseGroupId + '/controller_' + houseName + '/cooling_setpoint'
    #                         _log.info('controller agent {0} publishes updated setpoints {1} to house controlled with topic: {2}'.format(self.controller['name'], set_temp, pub_topic))
                        #Create timestamp
                        now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
                        headers = {
                            headers_mod.DATE: now
                        }
                        self.vip.pubsub.publish('pubsub', pub_topic, headers, set_temp)
                        
                    # Calculate bidding price
                    # Bidding price when monitored load temperature is at the min and max limit of the controller
                    bid_price = -1
                    no_bid = 0
                    if self.controller[houseName]['dir'] > 0:
                        if self.controller[houseName]['use_predictive_bidding'] == 1:
                            if powerstate == 'OFF' and monitor > (maxT - deadband_shift):
                                bid_price = self.aggregator['price_cap']
                            elif powerstate != 'OFF' and monitor < (minT + deadband_shift):
                                bid_price = 0
                                no_bid = 1
                            elif powerstate != 'OFF' and monitor > maxT:
                                bid_price = self.aggregator['price_cap']
                            elif powerstate == 'OFF' and monitor < minT:
                                bid_price = 0
                                no_bid = 1
                        else:
                            if monitor > maxT:
                                bid_price = self.aggregator['price_cap']
                            elif monitor < minT:
                                bid_price = 0
                                no_bid = 1
                    elif self.controller[houseName]['dir'] < 0:
                        if self.controller[houseName]['use_predictive_bidding'] == 1:
                            if powerstate == 'OFF' and monitor < (minT + deadband_shift):
                                bid_price = self.aggregator['price_cap']
                            elif powerstate != 'OFF' and monitor > (maxT - deadband_shift):
                                bid_price = 0
                                no_bid = 1
                            elif powerstate != 'OFF' and monitor < minT:
                                bid_price = self.aggregator['price_cap']
                            elif powerstate == 'OFF' and monitor > maxT:
                                bid_price = 0
                                no_bid = 1
                        else:
                            if monitor < minT:
                                bid_price = self.aggregator['price_cap']
                            elif monitor > maxT:
                                bid_price = 0
                                no_bid = 1
                    elif self.controller[houseName]['dir'] == 0:
                        if self.controller[houseName]['use_predictive_bidding'] == 1:
                            if not(direction):
                                warnings.warn('the variable direction did not get set correctly')
                            elif ((monitor > maxT + deadband_shift) or  (powerstate != 'OFF' and monitor > minT - deadband_shift)) and direction > 0:
                                bid_price = self.aggregator['price_cap']
                            elif ((monitor < minT - deadband_shift) or  (powerstate != 'OFF' and monitor < maxT + deadband_shift)) and direction < 0:
                                bid_price = self.aggregator['price_cap']
                            elif powerstate == 'OFF' and monitor > maxT:
                                bid_price = 0
                                no_bid = 1
                        else:
                            if monitor < minT:
                                bid_price = self.aggregator['price_cap']
                            elif monitor > maxT:
                                bid_price = 0
                                no_bid = 1
                            else:
                                bid_price = avgP
                    
                    # Bidding price when the monitored load temperature is within the controller temp limit
                    if monitor > setpoint0:
                        k_T = ramp_high
                        T_lim = range_high
                    elif monitor < setpoint0:
                        k_T = ramp_low
                        T_lim = range_low
                    else:
                        k_T = 0
                        T_lim = 0
                    
                    bid_offset = 0.0001
                    if bid_price < 0 and monitor != setpoint0:
                        if abs(stdP) < bid_offset:
                            bid_price = avgP
                        else:
                            bid_price = avgP + (monitor - setpoint0)*(k_T * stdP) / abs(T_lim)   
                    elif monitor == setpoint0:
                        bid_price = avgP
                    
                    # Update the outputs
                    if demand > 0 and no_bid != 1:
                        # Update bid price and quantity
                        self.controller[houseName]['last_p'] = bid_price
                        self.controller[houseName]['last_q'] = demand
                        # Check market unit with controller default unit kW
                        if (self.aggregator['market_unit']).lower() != "kW":
                            if (self.aggregator['market_unit']).lower() == "w":
                                self.controller[houseName]['last_q'] = self.controller[houseName]['last_q']*1000
                            elif (self.aggregator['market_unit']).lower() == "mw":
                                self.controller[houseName]['last_q'] = self.controller[houseName]['last_q']/1000
                        # Update parameters
                        self.controller_bid[houseName]['market_id'] = self.controller[houseName]['lastmkt_id']
                        self.controller_bid[houseName]['bid_price'] = self.controller[houseName]['last_p']
                        self.controller_bid[houseName]['bid_quantity'] = self.controller[houseName]['last_q']
                       
                        # Set controller_bid state
                        self.controller_bid[houseName]['state'] = powerstate
                            
                    else:
                        # Update bid price and quantity
                        self.controller[houseName]['last_p'] = 0
                        self.controller[houseName]['last_q'] = 0
                        # Update controller_bid parameters
                        self.controller_bid[houseName]['market_id'] = 0
                        self.controller_bid[houseName]['bid_price'] = 0
                        self.controller_bid[houseName]['bid_quantity'] = 0
                else:
                    raise ValueError('Currently only the ramp mode controller is defined')
                 
                # Update house last power state
                self.house[houseName]['last_pState'] = powerstate
                
                # Display the bid only when bidding quantity if not 0
                if self.controller_bid[houseName]['bid_quantity'] > 0:
                    _log.info('At time {0:s}, controller agent {5:s} bids with market_id {1:d}, bidding price is {2:f} $, bidding quantity is {3:f} kW, rebid is {4:d}'.format(self.controller[houseName]['t1'].strftime("%Y-%m-%d %H:%M:%S"), self.controller_bid[houseName]['market_id'], self.controller_bid[houseName]['bid_price'], self.controller_bid[houseName]['bid_quantity'], self.controller_bid[houseName]['rebid'], self.controller[houseName]['name']))
                
                # Issue a bid, if appropriate
                if self.controller_bid[houseName]['bid_quantity'] > 0.0 and self.controller_bid[houseName]['bid_price'] > 0.0:    
                    # Publish the changed setpoints:
                    # Create a message for all points.
                    all_message = [{'market_id': self.controller_bid[houseName]['market_id'], 
                                    'bid_id': self.controller[houseName]['name'], 
                                    'price': self.controller_bid[houseName]['bid_price'],
                                    'quantity': self.controller_bid[houseName]['bid_quantity'], 
                                    'bid_accepted': no_bid == 0, 
                                    'state': self.controller_bid[houseName]['state'],
                                    'rebid': self.controller_bid[houseName]['rebid'], 
                                    'bid_name': self.controller[houseName]['name']                              
                                    },
                                   {'market_id': {'units': 'none', 'tz': 'UTC', 'type': 'integer'},
                                    'bid_id': {'units': 'none', 'tz': 'UTC', 'type': 'string'}, 
                                    'price': {'units': '$', 'tz': 'UTC', 'type': 'float'},
                                    'quantity': {'units': 'kW', 'tz': 'UTC', 'type': 'float'},
                                    'bid_accepted': {'units': 'none', 'tz': 'UTC', 'type': 'boolean'}, 
                                    'state': {'units': 'none', 'tz': 'UTC', 'type': 'string'},
                                    'rebid': {'units': 'none', 'tz': 'UTC', 'type': 'integer'}, 
                                    'bid_name': {'units': 'none', 'tz': 'UTC', 'type': 'string'}                                
                                    }]
                    pub_topic = 'controller/controller_' + houseName + '/all'
                    _log.info('controller agent {0} publishes bids to aggregator with topic: {1}'.format(config['agentid'], pub_topic))
                    #Create timestamp
                    now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
                    headers = {
                        headers_mod.DATE: now
                    }
                    self.vip.pubsub.publish('pubsub', pub_topic, headers, all_message)
           
        #            print('  (temp,state,load,avg,std,clear,cap,init)',self.house[houseName]['currTemp'],self.house[houseName]['powerstate'],self.house[houseName]['controlled_load_all'],self.market['average_price'],self.market['std_dev'],self.market['clear_price'],self.market['price_cap'],self.market['initial_price'])      
        #            print (timeSim, 'Bidding PQSrebid',self.controller_bid[houseName]['bid_price'],self.controller_bid[houseName]['bid_quantity'],self.controller_bid[houseName]['state'],self.controller_bid[houseName]['rebid'])
                    # Set controller_bid rebid value to true after publishing
                    self.controller_bid[houseName]['rebid'] = 1
            
        # ====================Postsync content =========================== 
        def controller_postsync(self):
            ''' This method comes from the postsync part of the controller source code in GLD 
            '''         
            for oneHouse in houses:
                
                houseName = oneHouse.keys()
                if len(houseName) != 1:
                    raise ValueError('For each house, more than one house keys are given')
                else:
                    houseName = houseName[0]
                                
                # Update last setpoint if setpoint0 changed
                if self.controller[houseName]['control_mode'] == 'CN_RAMP' and self.controller[houseName]['last_setpoint'] != self.controller[houseName]['setpoint0']:
                    self.controller[houseName]['last_setpoint'] = self.controller[houseName]['setpoint0']
                     
                # Compare t1 with next_run 
    #             if self.controller[houseName]['t1'] < self.controller[houseName]['next_run'] - self.controller[houseName]['bid_delay']:
    #                 postsyncReturn = self.controller[houseName]['next_run'] - self.controller[houseName]['bid_delay']
    #                 return postsyncReturns  
    #             
    #             if self.controller[houseName]['t1'] - self.controller[houseName]['next_run'] < self.controller[houseName]['bid_delay']:
    #                 postsyncReturn = self.controller[houseName]['next_run']
                
                if self.controller[houseName]['t1'] >= self.controller[houseName]['next_run']:
                    self.controller[houseName]['next_run'] += datetime.timedelta(0,self.controller[houseName]['period'])
                    self.bidded[houseName] = False
              
    Agent.__name__ = config['agentid']
    return controllerAgent(**kwargs)        
                
def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(controller_agent)
    except Exception as e:
        print e
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
                  
                
                
                
                
                