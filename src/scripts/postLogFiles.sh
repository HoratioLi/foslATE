#!/bin/bash
# Script to run upload unposted log files
echo "Running logfile posting script..."
now=$(date +"%Y_%m_%d_%H%M_%S")
filename=log_script_output_$now.log
echo "Exporting script output as $filename"
cd /home/pi/misfit/Production/src/
(python /home/pi/misfit/Production/src/processLogFiles.py) 2>&1 | tee upload_log_script_output/$filename
