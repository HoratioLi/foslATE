import subprocess
import ast
from constants import *

def countMFGShinesWithThisSNAndNotIEEE(serial_number, ieee):
	#search through all mfg logs in dropbox for occurences of these 10 characters.
	cmdString = """grep '%s' %s -r""" % (serial_number, MFG_LOGS_PATH)
	try:
		result = subprocess.check_output([cmdString], shell=True)
		if result:

			#split them on new line
			results = result.split('\n')

			#grab only entries in the serial.log (ATE2) files.
			final_results = []
			for each in results:
				if "serial.log" in each:
					#split on the : so we only have the actual log data
					toAdd = each.split('serial.log:')[1]
					toAdd = toAdd.rstrip('\r')
					final_results.append(toAdd)

			print final_results
			#remove all identical log duplicates because these are just copies in different log files (not re-runs of the same serial #)
			final = list(set(final_results))
			
			#grab key 'shine_serial' from the log because it contains the serial programmed on the shine for that run of the ATE
			final_ieees = []
			for each in final:
				dictVersion = ast.literal_eval(each)
				if dictVersion['shine_serial'] == serial_number:
					final_ieees.append(dictVersion['ieee'])
			print ieee
			print final_ieees
			duplicate_count = 0
			for each in final_ieees:
				if each != ieee and each != '':
					duplicate_count+=1
		
			return duplicate_count
		else:
			return 0
	except:
		return 0

def countMFGShinesWithSNAndAnyIEEE(serial_number):
	#search through all mfg logs in dropbox for occurences of these 10 characters.
	cmdString = """grep '%s' %s -r""" % (serial_number, MFG_LOGS_PATH)
	try:
		result = subprocess.check_output([cmdString], shell=True)
		if result:

			#split them on new line
			results = result.split('\n')

			#grab only entries in the serial.log (ATE2) files.
			final_results = []
			for each in results:
				if "serial.log" in each:
					#split on the : so we only have the actual log data
					toAdd = each.split('serial.log:')[1]
					toAdd = toAdd.rstrip('\r')
					final_results.append(toAdd)

			print final_results
			#remove all identical log duplicates because these are just copies in different log files (not re-runs of the same serial #)
			final = list(set(final_results))
			
			#grab key 'shine_serial' from the log because it contains the serial programmed on the shine for that run of the ATE
			final_ieees = []
			for each in final:
				dictVersion = ast.literal_eval(each)
				if dictVersion['shine_serial'] == serial_number:
					final_ieees.append(dictVersion['ieee'])

			doops = []
			for each in final_ieees:
				if each != '':
					if each not in doops:
						doops.append(each)

			return len(doops)
		else:
			return 0
	except:
		return 0

def testLogFileForDoops():
	f = open('/Users/akilian/Dropbox/MisfitSharedHWScience/Return_Analysis/122_Batch_Dec20/unlink.log')
	shines = f.readlines()
	shines = shines[0].split('\r')
	print shines
	for shine in shines:
		print shine
		count = countMFGShinesWithSNAndAnyIEEE(shine)
		print count
		if count >= 2:
			doops_file = open('log/doops.log', 'a')
			try:
				doops_file.write(shine + '\n')
			finally:
				doops_file.close()

if __name__ == '__main__':
	if 1:
		testLogFileForDoops()

	if 0:
		serial = 'SH0AZ01UF7'
		ieee = '34.B1.F7.CF.C6.07'
		print "SEARCHING MFG LOGS FOR SERIAL #: %s" % serial
		
		doop_count = countMFGShinesWithThisSN(serial, ieee)

		if doop_count == 0:
			print "NO DUPLICATES FOR SERIAL: %s" % serial
		if doop_count >= 1:
			print "DUPLICATES FOUND FOR SERIAL: %s" % serial
