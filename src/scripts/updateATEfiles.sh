#!/bin/bash
# This script transfers files from the transfer directory to ATE

printf "Removing /usr/local/lib/python2.7/dist-packages/pyblehci/"
sudo rm -Rf /usr/local/lib/python2.7/dist-packages/pyblehci
printf "Removed."

printf "\n\nUnzipping pyblehci-master.zip\n\n"
cd /home/pi/misfit/ShineProduction/transferToPi/
rm -Rf __MACOSX/
rm -Rf pyblehci-master
unzip pyblehci-master.zip 
rm -Rf /home/pi/misfit/pyblehci

printf "\n\nReplacing existing pyblehci directory with new version\n\n"
mv /home/pi/misfit/ShineProduction/transferToPi/pyblehci-master /home/pi/misfit/pyblehci

printf "\n\nInstalling pyblehci\n\n"
cd /home/pi/misfit/pyblehci/
python setup.py install

printf "\n\nUpdating local_constants.py\n\n"
cd /home/pi/misfit/ShineProduction/src/
rm local_constants.py
cp /home/pi/misfit/ShineProduction/transferToPi/local_constants_master.py local_constants.py

printf "\n\nMoving runATE script to desktop\n\n"
cp /home/pi/misfit/ShineProduction/transferToPi/runATE.desktop /home/pi/Desktop/runATE.desktop

printf "\n\nMoving uploadLogFiles script to desktop\n\n"
cp /home/pi/misfit/ShineProduction/transferToPi/uploadLogFiles.desktop /home/pi/Desktop/uploadLogFiles.desktop

# This is just here temporarily
echo "Checking for log_posted and log_unposted directories..."
LOG_POSTED_DIR=/home/pi/misfit/ShineProduction/src/log_posted
LOG_UNPOSTED_DIR=/home/pi/misfit/ShineProduction/src/log_unposted
LOG_NO_POST_DIR=/home/pi/misfit/ShineProduction/src/log_no_post
LOG_UPLOAD_OUTPUT_DIR=/home/pi/misfit/ShineProduction/src/upload_log_script_output
PREV_TEST_DATA_DIR=/home/pi/misfit/ShineProduction/src/prev_test_data

if [ -d "$LOG_POSTED_DIR" ]; then
	echo $LOG_POSTED_DIR "already exists"
else
	echo "Creating" $LOG_POSTED_DIR
	mkdir $LOG_POSTED_DIR
fi

if [ -d "$LOG_UNPOSTED_DIR" ]; then
	echo $LOG_UNPOSTED_DIR "already exists"
else
	echo "Creating" $LOG_UNPOSTED_DIR
	mkdir $LOG_UNPOSTED_DIR
fi

if [ -d "$LOG_NO_POST_DIR" ]; then
	echo $LOG_NO_POST_DIR "already exists"
else
	echo "Creating" $LOG_NO_POST_DIR
	mkdir $LOG_NO_POST_DIR
fi

if [ -d "$LOG_UPLOAD_OUTPUT_DIR" ]; then
	echo $LOG_UPLOAD_OUTPUT_DIR "already exists"
else
	echo "Creating" $LOG_UPLOAD_OUTPUT_DIR
	mkdir $LOG_UPLOAD_OUTPUT_DIR
fi

if [ -d "$PREV_TEST_DATA_DIR" ]; then
	echo $PREV_TEST_DATA_DIR "already exists"
else
	echo "Creating" $PREV_TEST_DATA_DIR
	mkdir $PREV_TEST_DATA_DIR
fi

echo "Removing log_unposted entries with the incorrect format..."
ls $LOG_UNPOSTED_DIR/device*.log
rm $LOG_UNPOSTED_DIR/device*.log

printf "\n\nDone with setup script.\n\n"

