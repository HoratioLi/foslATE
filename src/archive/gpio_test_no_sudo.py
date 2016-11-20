#!/usr/bin/env python

import wiringpi2 as pi
from multiprocessing import Process
from subprocess import call

#only use this function in its own thread
#should only be called from write_gpio()
def process_write_gpio(bcm_pin, value):
	if value == "1":
		pi.digitalWrite(bcm_pin, 1)
	else:
		pi.digitalWrite(bcm_pin, 0)

#this function is used to setup the thread for gpio writes
#use this one from python code
def write_gpio(bcm_pin, value):
	p = Process(target=process_write_gpio, args=(bcm_pin, value))
	p.start()
	p.join()

	
call(["gpio", "export", "18", "out"])		#configure bcm pin 18 as an output
call(["gpio", "export", "17", "in"])		#configure bcm pin 17 as an input
call(["gpio", "-g", "mode", "17", "up"])	#configure bcm pin 17 to have a pull up resistor
pi.wiringPiSetupSys()				#setup gpio to work with no sudo. must be called after 'gpio export' and 'gpio mode' calls

choice = raw_input("Enter '0' for low and '1' for high >")
 
write_gpio(18,choice)				# example write of pin 18 of the user choice. choice must be 0 or 1

print(pi.digitalRead(18))
print(pi.digitalRead(17))

call(["gpio", "unexportall"])		#return gpio to raspi

print('just printing something to see if gets to end')

