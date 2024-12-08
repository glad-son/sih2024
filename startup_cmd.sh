#!/bin/bash

MAVROSLOGFILE="/home/raspberry/Desktop/MAVROS_LOG.txt"
RPLIDARLOGFILE="/home/raspberry/Desktop/RPLIDAR_LOG.txt"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $2
}

log_message "Starting MAVROS monitoring script" $MAVROSLOGFILE
log_message "Starting RPLIDAR monitoring script" $RPLIDARLOGFILE

source /opt/ros/jazzy/setup.bash >> $RPLIDARLOGFILE 2>&1
source /home/raspberry/ardu_ws/install/setup.sh >> $RPLIDARLOGFILE 2>&1

start_mavros() {
    log_message "Starting MAVROS script" $MAVROSLOGFILE
    ros2 launch mavros px4.launch >> $MAVROSLOGFILE 2>&1 &
    MAVROS_PID=$!
}

start_rplidar() {
    log_message "Starting RPLIDAR script" $RPLIDARLOGFILE
    ros2 launch rplidar_ros rplidar_a2m12_launch.py >> $RPLIDARLOGFILE 2>&1 &
    RPLIDAR_PID=$!
}

# Start both processes initially
start_mavros
start_rplidar

# Monitoring loop
while true; do
    # Check MAVROS process
    if ! kill -0 $MAVROS_PID 2>/dev/null; then
        log_message "MAVROS terminated, restarting..." $MAVROSLOGFILE
        start_mavros
    fi

    # Check RPLIDAR process
    if ! kill -0 $RPLIDAR_PID 2>/dev/null; then
        log_message "RPLIDAR terminated, restarting..." $RPLIDARLOGFILE
        start_rplidar
    fi

    # Check every 5 seconds
    sleep 5
done

