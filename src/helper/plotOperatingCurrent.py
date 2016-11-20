
#!/usr/bin/env python

import numpy as np
import pylab as plt
import matplotlib
import datetime
from helper.utils import *

file_path = '/home/pi/Desktop/operatingCurrent/'
# name_base = 'opCurrent'

# filetimestamp = datetime.datetime.utcnow().strftime("%Y_%m_%d_%H%M")   

def exportData(readings, column_headings, name_base, filetimestamp):

	filename = name_base + '_' + filetimestamp

	data = []
	data.append(column_headings)
	for i, reading in enumerate(readings):
		data.append([i, reading])

	if data:
		writeCSV(file_path, filename, data)

	return True

def exportFigure(readings, name_base, filetimestamp, labels):
	filename = name_base + '_' + filetimestamp
	target_file = generateFileName(file_path, filename, "png") + ".png"
	print 'Saving ' + target_file + '...'
	plt.ion()
	plt.figure()
	plt.plot(np.arange(1,len(readings)+1),readings,'b.-')
	plt.xlabel(labels['x_label'])
	plt.ylabel(labels['y_label'])
	plt.title(labels['title'])
	plt.savefig(target_file,dpi=200)	

	return True
