#!/bin/bash
# This script transfers files from the transfer directory to ATE

# Note: this only needs to be run once on each Pi
printf "\n\nInstalling PIL (python imaging library)"
cd /home/pi/misfit/Production/src/
pip install Pillow
sudo apt-get install tk8.5-dev tcl8.5-dev
pip install -I pillow

# printf "\n\nSetting clock time to China time\n\n"
# echo "TZ='Asia/Shanghai'; export TZ" >.profile

printf "\n\nSetting clock time to California time\n\n"
echo "TZ='America/Los_Angeles'; export TZ" >.profile

printf "\n\nCleaning up Desktop\n\n"
cd /home/pi/
sudo mkdir 'desktop items'
sudo mv Desktop/* desktop\ items/
sudo mv desktop\ items/lxterminal.desktop Desktop/
sudo mv desktop\ items/shutdown.desktop Desktop/
sudo mv desktop\ items Desktop

echo "Checking for log_posted and log_unposted directories..."
LOG_POSTED_DIR=/home/pi/misfit/Production/src/log_posted
LOG_UNPOSTED_DIR=/home/pi/misfit/Production/src/log_unposted
LOG_NO_POST_DIR=/home/pi/misfit/Production/src/log_no_post
LOG_UPLOAD_OUTPUT_DIR=/home/pi/misfit/Production/src/upload_log_script_output

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

printf "\n\nRunning setupATE script\n\n"
cd /home/pi/misfit/Production/src/
scripts/setupATEfiles.sh

printf "\n\nDone with setup script.\n\n"

