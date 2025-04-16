#!/bin/bash

# Is the Xbox Controller connected?
isControllerConnected=$(ls /dev/input | grep event9)

# Check if the Xbox Controller is connected.
if [ -n "$isControllerConnected" ]; then
  echo "Command produced isControllerConnected: $isControllerConnected"
  /usr/bin/python3 /home/seniordesign/Documents/Blackbriar/src/servoXbox.py &
  /usr/bin/python3 /home/seniordesign/Documents/Blackbriar/src/dcMotorxbox.py &
  while [ -n "$isControllerConnected" ]; do
    isControllerConnected=$(ls /dev/input | grep event9)
    echo "The Xbox Controller is still connected"
    sleep 1
  done
  echo "The Xbox Controller is no longer connected."
else
  echo "The Xbox Controller is not connected."
fi
