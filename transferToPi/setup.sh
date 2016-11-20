#!/bin/bash

#if there is no argument for $1 or it is invalid, print an error and exit setup.
#if $2 or $3 is not there, then set ATE_ID=1 and ATE_INDEX=0
if [ "$#" -ne 3 ]
then
	echo "Error: Invalid number of arguments. Use the following example:"
	echo "./setup.sh <Product_name> <ATE_ID> <ATE_INDEX>"
	echo "./setup.sh xyz_product_name 1 2"
	exit 1
fi

#if argument 1 does not match any of the known products, exit.

found_project=0   # Flag for finding project initialized to 0. If the project is found, set it to 1.
projects=$(grep projectList ../src/config/common.py | cut -d "=" -f 2)

for project in $projects
do
	device=$(echo $project | awk -F\" '{print $2}')

	if [[ $device == $1 ]] ; then
		found_project=1  # indicates project is found
	fi
done

if [ $found_project == 0 ] ; then
	echo "Invalid product name. Ensure that the product name is entered correctly."
	exit 2
fi

#if argument 2 is not equal to the list of known ATE_IDs then exit.
if [[ "$2" -ne "1" && "$2" != "1.5" && "$2" -ne "2" && "$2" -ne "3" ]] ; then
	echo "Error: Invalid ATE_ID" >&2; exit 3
fi

echo "Setting up $1 ATE $2-$3..."

# copy config files and set ATE_ID=$2, ATE_INDEX=$3, DEVICE_TYPE=$1 in ate_settings.py
echo "Updating ate_settings.py and local_settings.py"
sudo cp /home/pi/misfit/ShineProduction/transferToPi/ate_settings_master.py /home/pi/misfit/ShineProduction/src/ate_settings.py
sudo cp /home/pi/misfit/ShineProduction/transferToPi/local_constants_master.py /home/pi/misfit/ShineProduction/src/local_constants.py

product=$1
id=$2
index=$3

# The directory path to the ate_settings.py file.
ATE_SETTINGS=/home/pi/misfit/ShineProduction/src/ate_settings.py

# Update the STATION_ID and STATION_INDEX with the passed in arguments.
sed -i 's/ID=1/ID='$id'/' $ATE_SETTINGS
sed -i 's/INDEX=0/INDEX=\"'$index'\"/' $ATE_SETTINGS

# Append the DEVICE_TYPE to the end of the ate_settings.py file.
DEVICE="DEVICE_TYPE=\"$product\""
echo $DEVICE >> $ATE_SETTINGS

echo "Finished updating files."

# pexpect is used to read terminal output.  This module is used when mounting shared drives and in the segger module when ATE is updating the Flasher with new firmware.
echo "Installing pexpect..."
pip install pexpect

# This module is required for making SOAP calls.
echo "Installing pysimplesoap..."
pip install pysimplesoap

# This .rule file is required for communication with the SEGGER flasher.
echo "Copying JLink rules..."
sudo cp /home/pi/misfit/ShineProduction/src/segger/99-jlink.rules /etc/udev/rules.d/

# This file configures the GPIO pins of Raspberry Pi to a known safe mode when used with the Lunchbox hardware.  If the pins are not configure correctly, Lunchbox could potentially be damaged.
echo "Configuring for GPIO safe mode..."
sudo cp /home/pi/misfit/ShineProduction/transferToPi/rc.local /etc/rc.local

# Copy the icon of the runATEUpdater application to the desktop.
echo "Creating runATEUpdater shortcut..."
cp /home/pi/misfit/ShineProduction/transferToPi/runATEUpdater.desktop /home/pi/Desktop/

# Reboot the system for changes to take effect.
echo "Rebooting system..."
sudo reboot
