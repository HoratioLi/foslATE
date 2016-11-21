#!/bin/bash
# This script transfers files from the transfer directory to ATE

printf "\n\nReplacing local_constants.py\n\n"
cd /home/pi/misfit/Production/src/
rm local_constants.py
cp /home/pi/misfit/Production/transferToPi/local_constants_master.py local_constants.py

printf "\n\nDone with setup script.\n\n"

