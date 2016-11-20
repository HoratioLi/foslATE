#!/bin/bash

printf "\n\nReplacing existing pyblehci directory with new version\n\n"
cp -r /home/pi/misfit/ShineProduction/transferToPi/pyblehci-master/* /home/pi/misfit/pyblehci

printf "\n\nInstalling pyblehci\n\n"
cd /home/pi/misfit/pyblehci/
python setup.py install

printf "\nCompleted installing BLE files\n"