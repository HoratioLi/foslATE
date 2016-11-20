#!/usr/bin/env python

from gpio_no_sudo import *

gpio_ns_init()

choice = raw_input("Enter '0' for low and '1' for high >")
 
gpio_ns_write(24,choice)				# example write of pin 18 of the user choice. choice must be 0 or 1

print(gpio_ns_read(24))
print(gpio_ns_read(23))

gpio_ns_pull(23, "down")

print(wiringpi2.digitalRead(24))
print(wiringpi2.digitalRead(23))

gpio_ns_release()

choice = raw_input("Enter '0' for low and '1' for high >")

print('just printing something to see if gets to end')
