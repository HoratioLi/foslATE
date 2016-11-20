#!/bin/bash
# Script to check/create directory for operating current data
echo "Checking for operating current data directory..."

DIRECTORY=/home/pi/Desktop/operatingCurrent
IMG_DIRECTORY=/home/pi/Desktop/operatingCurrent/png
CSV_DIRECTORY=/home/pi/Desktop/operatingCurrent/csv

if [ -d "$DIRECTORY" ]; then
	echo $DIRECTORY "already exists"
else
	echo "Creating" $DIRECTORY 
	mkdir $DIRECTORY
fi

if [ -d "$IMG_DIRECTORY" ]; then
	echo $IMG_DIRECTORY "already exists"
else
	echo "Creating" $IMG_DIRECTORY 
	mkdir $IMG_DIRECTORY
fi

if [ -d "$CSV_DIRECTORY" ]; then
	echo $CSV_DIRECTORY "already exists"
else
	echo "Creating" $IMG_DIRECTORY 	
	mkdir $CSV_DIRECTORY
fi

