#!env/bin/python
# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:

# Copyright (c) 2015, Battelle Memorial Institute
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation
# are those of the authors and should not be interpreted as representing
# official policies, either expressed or implied, of the FreeBSD
# Project.
#
# This material was prepared as an account of work sponsored by an
# agency of the United States Government.  Neither the United States
# Government nor the United States Department of Energy, nor Battelle,
# nor any of their employees, nor any jurisdiction or organization that
# has cooperated in the development of these materials, makes any
# warranty, express or implied, or assumes any legal liability or
# responsibility for the accuracy, completeness, or usefulness or any
# information, apparatus, product, software, or process disclosed, or
# represents that its use would not infringe privately owned rights.
#
# Reference herein to any specific commercial product, process, or
# service by trade name, trademark, manufacturer, or otherwise does not
# necessarily constitute or imply its endorsement, recommendation, or
# favoring by the United States Government or any agency thereof, or
# Battelle Memorial Institute. The views and opinions of authors
# expressed herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY
# operated by BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
# under Contract DE-AC05-76RL01830

#}}}
from datetime import datetime
import time
import os
import sys

import json
import gevent
import logging
import warnings
import re
from collections import defaultdict

from gevent.core import callback

from volttron.platform.messaging import headers as headers_mod
from volttron.platform.vip.agent import Agent, PubSub, Core
from volttron.platform.agent import utils
import common

#FNCS inports
import fncs

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = "1.0"

def remote_url(**kwargs):
    return "{vip_address}:{port}?serverkey={server_key}" \
        "&publickey={agent_public}&" \
        "secretkey={agent_secret}".format(**kwargs)

class FNCS_VOLTTRON_Bridge(Agent):
    
    def __init__(self,  simulation_run_time, 
                        heartbeat_period,
                        heartbeat_multiplier,
                        fncs_zpl,
                        **kwargs):
        super(FNCS_VOLTTRON_Bridge,self).__init__(**kwargs)
        self.simtime = 0
        self.heartbeat_period = heartbeat_period
        self.heartbeat_multiplier = heartbeat_multiplier
        self.fncs_zpl = fncs_zpl
        self.subscriptionVoltron = {}
        inTime = 0
        inUnit = ''
        timeMuliplier = 0
        
        parsedTime = re.findall(r'(\d+)(\s?)(\D+)', simulation_run_time)
        if len(parsedTime) > 0:
            inTime = int(parsedTime[0][0])
            inUnit = parsedTime[0][2]
            if 's' in inUnit[0] or 'S' in inUnit[0]:
                timeMultiplier = 1
            elif 'm' in inUnit[0] or 'M' in inUnit[0]:
                timeMultiplier = 60
            elif 'h' in inUnit[0] or 'H' in inUnit[0]:
                timeMultiplier = 3600
            elif 'd' in inUnit[0] or 'D' in inUnit[0]:
                timeMultiplier = 86400
            else:
                warnings.warn("Unknown time unit supplied. Defaulting to seconds.")
                timeMultiplier = 1
        else:
            raise RuntimeError("Unable to parse run time argument. Please provide run time in the following format: #s, #m, #h, #d, or #y.")
        self.simlength = inTime*timeMultiplier
        self.simStart = datetime.utcnow()
        

    def onmessage(self, peer, sender, bus, topic, headers, message):
        d = {'topic': topic, 'headers': headers, 'message': message}
        # Forward message to FNCS
        if not fncs.is_initialized():
            raise RuntimeError("FNCS connection was terminated. Killing Bridge.")
        fncsmessage = str(message)
        # print 'Recieve from Volttron bus object ' + fncsmessage + 'with topic ' + topic
        topic = topic.replace('fncs/input/','').split('/')
        objName = topic[0]
        objProp = topic[1]
        if objName not in self.subscriptionVoltron.keys():
            self.subscriptionVoltron[objName] = {}
            # print "self.subscriptionVoltron becomes: " + str(self.subscriptionVoltron)
        if objProp not in self.subscriptionVoltron[objName].keys():
            self.subscriptionVoltron[objName][objProp] = None
        self.subscriptionVoltron[objName][objProp] = float(fncsmessage)
        # print "self.subscriptionVoltron becomes: " + str(self.subscriptionVoltron)
        print "Recieve from Volttron bus object " + objName + " property " + objProp + " with mesage:", fncsmessage
        _log.info('Recieve from Volttron bus object ' + objName + ' property ' + objProp + ' with mesage:' + str(fncsmessage))
        # fncs.publish(topic, fncsmessage)
        # _log.debug('Volttron->FNCS:\nTopic:%s\nMessage:%s\n'%(topic, message))
        

    @Core.receiver('onstart')
    def start(self, sender, **kwargs):
        self.vip.pubsub.subscribe(peer = 'pubsub',
                                  prefix = 'fncs/input/',
                                  #prefix = '',
                                  callback = self.onmessage).get(timeout=5)
        #Register with FNCS
        cfg = "name = {0[name]}\ntime_delta = {0[time_delta]}\nbroker = {0[broker]}\naggregate_sub = yes\n".format(self.fncs_zpl)
        if 'values' in self.fncs_zpl.keys():
            cfg += "values"
            for x in self.fncs_zpl['values'].keys():
                cfg += "\n    {0}\n        topic = {1[topic]}\n        defualt = {1[default]}\n        type = {1[type]}\n        list = {1[list]}".format(x,self.fncs_zpl['values'][x])
        fncs.initialize(cfg)
        # print "fncs_initialization: ", cfg
        if not fncs.is_initialized():
            raise RuntimeError("FNCS connection failed!")
        self.publish_heartbeat()
        print(self.heartbeat_period)
        self.core.periodic(self.heartbeat_period, self.publish_heartbeat)

    def publish_heartbeat(self):
        '''Send heartbeat message every HEARTBEAT_PERIOD seconds.

        HEARTBEAT_PERIOD is set and can be adjusted in the settings module.
        '''
        now = datetime.utcnow().isoformat(' ') + 'Z'
        nowdate = datetime.utcnow()
        print "publish_heartbeat", now
        timeDiff = nowdate - self.simStart
        valMap = defaultdict(dict)
        metaMap = defaultdict(dict)
        headers = {headers_mod.TIMESTAMP: now, headers_mod.DATE: now}
        #Tell FNCS we are at our next timestep
        if not fncs.is_initialized():
            raise RuntimeError("FNCS connection was terminated. Killing Bridge.")
        elif self.simtime > self.simlength:
            fncs_bridge_termination_topic = self.fncs_zpl['name']+'/simulation_end'
            fncsmessage = ['True', {'units' : 'NA', 'tz' : 'UTC', 'type': 'String'}]
            self.vip.pubsub.publish('pubsub', fncs_bridge_termination_topic, headers, fncsmessage)
            fncs.finalize()
            self.core.stop() # Stop the agent
        elif timeDiff.seconds >= 1:
            time1 = time.time()

            self.simtime+=self.heartbeat_period*self.heartbeat_multiplier
            print "fncs.time_request(",self.simtime,") request"

            time3 = time.time()
            self.simtime = fncs.time_request(self.simtime)
            time4 = time.time()
            print "it takes ", str(time4-time3), " seconds to process fncs time_request"
            _log.info('it takes ' + str(time4-time3) + ' seconds to process fncs time_request') 

            print "fncs.time_request() response", self.simtime
            #Grab Subscriptions from FNCS to publish to Volttron message bus
            subKeys = fncs.get_events()
            if len(subKeys) > 0:
                print "Values recieved from fncs.time_request()", self.simtime
                for x in subKeys:

                    time5 = time.time()
                    valStr = fncs.get_value(x)
                    time7 = time.time()
                    print "it takes ", str(time7-time5), " seconds to call function fncs.get_value()"

                    # print "the string recieved from fncs is: ", valStr
                    # _log.info('the string recieved from fncs is:' + valStr)
                    #parse message to split value and unit
                    valList = valStr.split(' ')
                    if len(valList) == 1:
                        val = valList[0]
                        valUnit = '';
                        try:
                            val = float(val)
                        except:
                            pass
                    elif len(valList) == 2:
                        val = valList[0]
                        valUnit = valList[1]
                        if 'int' in self.fncs_zpl['values'][x]['type']:
                            val = int(val)
                        elif 'double' in self.fncs_zpl['values'][x]['type']:
                            val = float(val)
                        elif 'complex' in self.fncs_zpl['values'][x]['type']:
                            raise RuntimeError("complex data type is currently not supported in Volttron.")
                        #TODO: come up with a better way to handle all types that can come in from fncs
                    else:
                        warnings.warn("FNCS message could not be parsed into value and unit. The message will be farwarded to Volttron message bus as is.")
                        val = valStr
                        valUnit = ''
                    fncsmessage = [val, {'units' : '{0}'.format(valUnit), 'tz' : 'UTC', 'type': '{0[type]}'.format(self.fncs_zpl['values'][x])}]
                    fncsTopic = common.FNCS_OUTPUT_PATH(path = 'devices/{0[topic]}'.format(self.fncs_zpl['values'][x])) #fncs/output/devices/topic

                    time8 = time.time()
                    print "it takes ", str(time8-time7), " seconds to process the message"

                    self.vip.pubsub.publish('pubsub', fncsTopic, headers, fncsmessage)
                    # print "publish to Volttron 1:", fncsTopic, fncsmessage
                    # _log.debug('FNCS->Volttron:\nTopic:%s\n:Message:%s\n'%(fncsTopic, str(fncsmessage)))
                    # device, point = self.fncs_zpl['values'][x]['topic'].rsplit('/', 1)
                    # print "device name is:", device
                    # print "point name is:", point
                    # deviceAllTopic = common.FNCS_OUTPUT_PATH(path = 'devices/' + device + '/all')
                    # valMap[deviceAllTopic][point] = val
                    # metaMap[deviceAllTopic][point] = fncsmessage[1]

                    time6 = time.time()
                    print "it takes ", str(time6-time8), " seconds to publish one string"
                    _log.info('it takes ' + str(time6-time5) + ' seconds to process one string')

                # for k in valMap.keys():
                #     allMessage = [valMap[k], metaMap[k]]
                    # self.vip.psubsub.publish('pubsub', k, headers, allMessage).get(timeout=5)
                    # print "publish to Volttron 2:", k, allMessage
                    # _log.debug('FNCS->Volttron:\nTopic:%s\n:Message:%s\n'%(k, str(allMessage)))
            
                time2 = time.time()
                # print "it takes ", str(time2-time4), " seconds to process fncs->volttron messages"
                # _log.info('the string recieved from fncs is:' + valStr)
                # _log.info('it takes ' + str(time2-time4) + ' seconds to process all fncs->volttron messages')

            else:
                print "Did not receive anything from fncs.time_request()", self.simtime        
                
        #Publish heartbeat message to voltron bus        
        # self.vip.pubsub.publish(
        #     'pubsub', '{0[name]}/heartbeat'.format(self.fncs_zpl), headers, now).get(timeout=5)


        # Periodically publish the subscribed messages from volttron back to FNCS then to GLD
        topic = "fncs_Test/fncs_input"
        if self.subscriptionVoltron:
            fncsmessage = {"fncs_Test": self.subscriptionVoltron}
            fncs.publish_anon(topic, json.dumps(fncsmessage))
            _log.debug('Volttron->FNCS:\nTopic: %s\n Message: %s\n'%(topic, fncsmessage))
            print 'Volttron->FNCS: Topic: ' + topic + 'Message: ' + str(fncsmessage)
            self.subscriptionVoltron = {}
    
def fncs_bridge(**kwargs): 
    # Read input variables
    # if (len(sys.argv) == 4):
    #     prefixVal = sys.argv[1]
    #     configFileName = sys.argv[2]
    #     BridgeId = sys.argv[3]

    #
    config = utils.load_config('FNCS_VOLTTRON_Bridge.config')
    heartbeat_period = config.get('heartbeat_period', 1)
    heartbeat_multiplier = config.get('heartbeat_multiplier', 1)
    fncs_zpl = config["fncs_zpl"]
    params = config["remote_platform_params"]
    simulation_run_time = config.get("simulation_run_time", "1h")
    identityName = 'FNCS_Volttron_Bridge'
    return FNCS_VOLTTRON_Bridge(
                                simulation_run_time, 
                                heartbeat_period,
                                heartbeat_multiplier,
                                fncs_zpl,
                                address=remote_url(**params),
                                identity=identityName)

def main():
    '''Main method to start the agent'''
    utils.vip_main(fncs_bridge)
    
if  __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        if fncs.is_initialized():
            fncs.die()
        pass
