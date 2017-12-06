#!/bin/bash
export VOLTTRON_HOME=$HOME/.volttron
export TAG1="controllerAgent"
export CONFIGS1="../ControllerAgent/config/*.cfg"
export SOURCE1="../ControllerAgent"

# Stop the controller agents in each group (totall 11 groups)
# for i in `seq 1 11`;
# do
#     tag=$TAG1
#     tag+=$i     
#     echo $tag
#     vctl stop --tag "$tag"
# done 

# # Remove the controller agents in each group (totall 11 groups)
# for i in `seq 1 11`;
# do
#     tag=$TAG1
#     tag+=$i     
#     echo $tag
#     vctl remove --tag "$tag"
# done 

# vctl stop --tag "$TAG1"
# vctl remove -f --tag "$TAG1"
# count=$1
# group=$1
# for filename in $CONFIGS1; do
#          (( count = count + 1))
#          if (( count == 50 ))
#          then
#      		sleep 1
#      		((group = group + 1))
#      		count=$1
#          fi
#          tag=$TAG1
#          tag+=$group
#          python ../../scripts/install-agent.py -s "$SOURCE1" -c "$filename" --tag "$tag"
# done

export TAG2="aggregatorAgent"
export CONFIGS2="../AggregatorAgent/config/*.cfg"
export SOURCE2="../AggregatorAgent"
vctl stop --tag "$TAG2"
vctl remove -f --tag "$TAG2"
for filename in $CONFIGS2; do
         python ../../scripts/install-agent.py -s "$SOURCE2" -c "$filename" --tag "$TAG2"
done

export TAG3="coordinatorAgent"
export CONFIGS3="../CoordinatorAgent/config/*.cfg"
export SOURCE3="../CoordinatorAgent"
vctl stop --tag "$TAG3"
vctl remove -f --tag "$TAG3"
# for filename in $CONFIGS3; do
#          python ../../scripts/install-agent.py -s "$SOURCE3" -c "$filename" --tag "$TAG3"
# done
