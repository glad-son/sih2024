#!/bin/bash

PID1=$(pgrep -f "ros2 launch mavros px4.launch")

PID2=$(pgrep -f "ros2 launch rplidar_ros rplidar_a2m12_launch.py")

if [ ! -z "$PID1" ];  then
	echo "Killing px4.launch"
	kill $PID1
else
	echo "px4.launch not running"
fi

if [ ! -z "$PID2" ];  then
        echo "Killing rplidar script"
        kill $PID2
else
        echo "rplidar script not running"
fi
