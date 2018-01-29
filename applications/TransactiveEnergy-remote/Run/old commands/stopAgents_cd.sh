#!/bin/bash
export TAG1="controllerAgent"
export TAG2="aggregatorAgent"
export TAG3="coordinatorAgent"

# Stop the controller agents in each group (totall 11 groups)
# for i in `seq 1 20`;
# do
# 	tag=$TAG1
#     tag+=$i		
#     echo $tag
#     vctl stop --tag "$tag"
# done 

count=$1
filename="$HOME/git/volttron/status.log"
while read -r line
do
	(( count = count + 1))
    if (( count == 25 ))
    then
 		sleep 1
 		((group = group + 1))
 		count=$1
    fi
    name="$line"
    echo "Name read from file - $name"
    stringarray=($name)
    echo ${stringarray[0]}
    uuid=${stringarray[0]}
    vctl remove "$uuid"
done < "$filename"


# count=$1
# while IFS='' read -r line || [[ -n "$line" ]]; do
# 	(( count = count + 1))
#     if (( count == 25 ))
#     then
#  		sleep 1
#  		((group = group + 1))
#  		count=$1
#     fi
#     echo "Text read from file: $line"
#     stringarray=($line)
#     echo ${stringarray[0]}
#     uuid=${stringarray[0]}
#     # vctl stop "$uuid"
# done < "$1"

# vctl stop --tag "$TAG1"
# vctl stop --tag "$TAG2"
# vctl stop --tag "$TAG3"
