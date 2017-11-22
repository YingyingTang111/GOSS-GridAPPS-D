#!/bin/bash
export TAG1="controllerAgent"
export TAG2="aggregatorAgent"
export TAG3="coordinatorAgent"

# run the controller agents in each group (totall 20 groups)
# for i in `seq 1 20`;
# do
# 	tag=$TAG1
#     tag+=$i		
#     echo $tag
#     vctl stop --tag "$tag"
# done 

# count=$1
# while IFS='' read -r line || [[ -n "$line" ]]; do
# 	(( count = count + 1))
#      if (( count == 25 ))
#      then
#  		sleep 1
#  		((group = group + 1))
#  		count=$1
#      fi
#     echo "Text read from file: $line"
#     stringarray=($line)
#     echo ${stringarray[0]}
#     uuid=${stringarray[0]}
#     # vctl start "$uuid"
# done < "$1"


# vctl stop --tag "$TAG1"
vctl stop --tag "$TAG2"
# vctl stop --tag "$TAG3"


# Start
# Start the controller agents in each group (totall 11 groups)
for i in `seq 1 20`;
do
	tag=$TAG1
    tag+=$i		
    echo $tag
    vctl start --tag "$tag"
    sleep 1
done 

# vctl start --tag "$TAG1"
vctl start --tag "$TAG2"
# vctl start --tag "$TAG3"
