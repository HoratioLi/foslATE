#!/bin/bash
# Script to run station tests from command line
echo "Running station tests from bash script..."
cd /home/pi/misfit/ShineProduction/src/
echo "serial_num: " $1
echo "serial_num_internal: " $2
echo "serial_num_smt: " $3
echo ""
python /home/pi/misfit/ShineProduction/src/runStationTests.py $1 $2 $3