#!/bin/bash

# START_TIME=$SECONDS
# export VOLTTRON_HOME=$HOME/.volttron
# export TAG1="controllerAgent"
# export CONFIGS1="../ControllerAgent/config/*.cfg"
# export SOURCE1="../ControllerAgent"
# # vctl stop --tag "$TAG1"
# # vctl remove -f --tag "$TAG1"
# count=$1
# group=1
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
#          echo $tag
#          # python ../../scripts/install-agent.py -s "$SOURCE1" -c "$filename" --tag "$tag"
# done

# for i in `seq 1 11`;
# do
#         echo $i
# done 

# export TAG1="controllerAgent"
# vctl stop --tag "$TAG1"
# vctl remove -f --tag "$TAG1"

# # Stop the controller agents in each group (totall 11 groups)
# for i in `seq 1 10`;
# do
# 	tag=$TAG1
#     tag+=$i		
#     echo $tag
#     vctl remove --tag "$tag"
#     sleep 1
# done 

while IFS='' read -r line || [[ -n "$line" ]]; do
    echo "Text read from file: $line"
    stringarray=($line)
    echo ${stringarray[0]}
    uuid=${stringarray[0]}
    # vctl remove "$uuid"
    sleep 1
done < "$1"