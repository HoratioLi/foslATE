#!/bin/bash
# This script transfers files from the transfer directory to ATE

printf "\n\nAdding ate_settings.py\n\n"
cd /home/pi/misfit/ShineProduction/src/
sudo cp /home/pi/misfit/ShineProduction/transferToPi/ate_settings_master.py ate_settings.py

# Setup cron script
cd /home/pi/misfit/ShineProduction/src/
scripts/setupCronLogPosts.sh

printf "\n\nRunning updateATE script\n\n"
cd /home/pi/misfit/ShineProduction/src/
scripts/updateATEfiles.sh

printf "\n\nDone with setup script.\n\n"

