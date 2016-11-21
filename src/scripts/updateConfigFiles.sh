#!/bin/bash
# This file updates ate_settings.py and local_settings.py

echo "Updating ate_settings.py and local_settings.py"
sudo cp /home/pi/misfit/Production/transferToPi/ate_settings_master.py /home/pi/misfit/Production/src/ate_settings.py
sudo cp /home/pi/misfit/Production/transferToPi/local_constants_master.py /home/pi/misfit/Production/src/local_constants.py
echo "Update complete."