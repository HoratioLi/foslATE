#!/usr/bin/env python

import usbtmc

instr = usbtmc.Instrument(2391, 6663)

instr.write("CONF:CURR:DC")
instr.write("CURR:DC:RANGE 0.01")
print(instr.ask("READ?"))

