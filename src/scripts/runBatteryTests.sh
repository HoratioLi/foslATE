#!/bin/bash
# Script to run battery tests from command line
echo "Running battery tests from bash script..."
cd /home/pi/misfit/Production/src/
echo "serial_num: " $1
echo "startDateStr: " $2
echo "endDateStr: " $3
echo ""
python /home/pi/misfit/Production/src/runBatteryTests.py $1 $2 $3