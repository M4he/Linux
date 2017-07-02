#!/bin/bash
#
# Toggles PulseAudio low latency loopback by starting/stopping
# a corresponding pacat process; enables loopback across devices
#
INP="alsa_input.pci-0000_00_1b.0.analog-stereo"
OUT="alsa_output.usb-FiiO_DigiHug_USB_Audio-01.analog-stereo"
LAT="10"

# check if process is already running
pgrep -f "^sh.*pacat"
STATE=$?
# if return code equals 0 -> process is running
if [ $STATE -eq 0 ]
then
    echo "stopping loopback process"
    pkill -f "^pacat"
    echo "killed loopback process"
else
    echo "starting loopback process"
    nohup sh -c "pacat -r --latency-msec=$LAT -d $INP | pacat -p --latency-msec=$LAT -d $OUT" &
    echo "started loopback process"
fi
