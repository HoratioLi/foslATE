import ast
import sys
from returncodes import *

failTotals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def usage():
	print "python analyze_return_log.py <path_to_return_log_file>"

def run(path):

	if len(path) != 1:
		usage()

	return_file = path[0]

	try:
		logFile = open(return_file, 'r')
	except IOError:
		print "Error: File does not appear to exist."
		sys.exit(1)

	a = 0
	for log in logFile.readlines():
		a+=1
		dictionaryLog = stringToDictionary(log)
		failures = dictionaryLog['failures']
		i = 0
		if failures[SN_MISMATCH_FAIL] == 1:
			print dictionaryLog
			print str(failures)
		while i < len(failures):
			failTotals[i] += failures[i]
			i+=1

	fails = 0
	for each in failTotals:
		fails += each
	print "TOTAL PROCESSED: " + str(a)
	print "TOTAL FAILS: " + str(fails)
	print "BREAKDOWN"
	print "SCAN_FAIL: " + str(failTotals[SCAN_FAIL])
	print "CHECK_FW_FAIL: " + str(failTotals[CHECK_FW_FAIL])
	print "ACCEL_STREAM_FAIL: " + str(failTotals[ACCEL_STREAM_FAIL])
	print "SN_DEFAULT_FAIL: " + str(failTotals[SN_DEFAULT_FAIL])
	print "SN_MISMATCH_FAIL: " + str(failTotals[SN_MISMATCH_FAIL])
	print "TIMEOUT_FAIL: " + str(failTotals[TIMEOUT_FAIL])
	print "AVG_CURRENT_FAIL: " + str(failTotals[AVG_CURRENT_FAIL])
	print "SN_DUPLICATE_FAIL: " + str(failTotals[SN_DUPLICATE_FAIL])
	print "RECENTLY_SYNCED_FAIL: " + str(failTotals[RECENTLY_SYNCED_FAIL])
	print "BATTERY_PLOT_FAIL: " + str(failTotals[BATTERY_PLOT_FAIL])

def stringToDictionary(line):
	diction = ast.literal_eval(line)
	if diction['ieee']:
		if diction['ieee'][0:2] == '09':
			diction['ieee'] = reverseIEEE(diction['ieee'])
		diction['ieee'] = diction['ieee'].translate(None, '.')
	return diction

if __name__ == '__main__':
	run(sys.argv[1:])