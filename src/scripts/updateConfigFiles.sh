#!/bin/bash
# This file updates ate_settings.py and local_settings.py

echo "Updating ate_settings.py and local_settings.py"
sudo cp /home/pi/misfit/ShineProduction/transferToPi/ate_settings_master.py /home/pi/misfit/ShineProduction/src/ate_settings.py
sudo cp /home/pi/misfit/ShineProduction/transferToPi/local_constants_master.py /home/pi/misfit/ShineProduction/src/local_constants.py
echo "Update complete."