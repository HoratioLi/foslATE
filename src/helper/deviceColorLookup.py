'''
Created on 2014-08-06

@author: Rachel Kalmar
'''

from constants import *

def deviceColorLookup(serial_num):

	if STATION_ID == 1:
		print "No device color information for Station 1."
		return None

	colorCode = serial_num[3]	

	if colorCode == 'Z' and STATION_ID != 1 and DEVICE_TYPE != "Silvretta":
		print "Warning, serial number ""%s"" is internal serial number, no color information available\n" % serial_num
		return None
	elif DEVICE_TYPE == 'Venus' and colorCode in colorMapVenus:
		color = colorMapVenus[colorCode]
	elif (DEVICE_TYPE == 'Apollo' or DEVICE_TYPE == 'SaturnMKII') and colorCode in colorMapApollo:
		color = colorMapApollo[colorCode]		
	elif DEVICE_TYPE == 'Aquila' and colorCode in colorMapAquila:
		color = colorMapAquila[colorCode]
	elif DEVICE_TYPE == 'Pluto' and colorCode in colorMapPluto:
		color = colorMapPluto[colorCode]
	elif DEVICE_TYPE == 'BMW' and colorCode in colorMapBMW:
		color = colorMapBMW[colorCode]		
	elif DEVICE_TYPE == 'Silvretta' and colorCode in colorMapSilvretta:
		color = colorMapSilvretta[colorCode]		
	else:
		print "Warning, color code ""%s"" for %s unknown.\n" % (colorCode, DEVICE_TYPE)
		color = None
	return color