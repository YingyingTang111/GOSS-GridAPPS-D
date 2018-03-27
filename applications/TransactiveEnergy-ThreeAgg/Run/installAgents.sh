#!/bin/bash
# export VOLTTRON_HOME=$HOME/.volttron1 - # This is to run instakl the agents in other volttron platform volttron1
export TAG1="controllerAgent"
export CONFIGS1="../ControllerAgent/config/*.cfg"
export SOURCE1="../ControllerAgent"
vctl stop --tag "$TAG1"
vctl remove -f --tag "$TAG1"
# count=$1
# group=$1
for filename in $CONFIGS1; do
         python ../../scripts/install-agent.py -s "$SOURCE1" -c "$filename" --tag "$TAG1"
done

export TAG2="aggregatorAgent"
export CONFIGS2="../AggregatorAgent/config/*.cfg"
export SOURCE2="../AggregatorAgent"
vctl stop --tag "$TAG2"
vctl remove -f --tag "$TAG2"
for filename in $CONFIGS2; do
         python ../../scripts/install-agent.py -s "$SOURCE2" -c "$filename" --tag "$TAG2"
done

export TAG3="coordinatorAgent"
# export CONFIGS3="../CoordinatorAgentPowerBalance/config/*.cfg"
# export SOURCE3="../CoordinatorAgentPowerBalance"
export CONFIGS3="../CoordinatorAgent/config/*.cfg"
export SOURCE3="../CoordinatorAgent"
vctl stop --tag "$TAG3"
vctl remove -f --tag "$TAG3"
for filename in $CONFIGS3; do
         python ../../scripts/install-agent.py -s "$SOURCE3" -c "$filename" --tag "$TAG3"
done
