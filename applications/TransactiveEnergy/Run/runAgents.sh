#!/bin/bash
export TAG1="controllerAgent"
export TAG2="aggregatorAgent"
export TAG3="coordinatorAgent"
vctl stop --tag "$TAG1"
vctl stop --tag "$TAG2"
# vctl stop --tag "$TAG3"
vctl start --tag "$TAG1"
vctl start --tag "$TAG2"
# vctl start --tag "$TAG3"
