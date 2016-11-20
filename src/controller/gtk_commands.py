#! /usr/bin/env python

'''
Created on 2015-12-24
@author: James Quen
'''

from pysimplesoap.client import SoapClient

def CommitTestDataToMES(sn=None, stationCode=None, stationDesc=None, sectionCode=None, sectionDesc=None, lineCode=None, 
						lineName=None, tester=None, test_time=None, testResult=0, ResultType=0, errorCode=None, errorDesc=None,
						testdata=None, testFileName=None, testFileByte=None):
    try:
        client = SoapClient(wsdl='http://10.10.32.54:8080/webservice/Wip_TestSvr.asmx?WSDL')

        response = client.CommitTestDataToMES(sn=sn, stationCode=stationCode, stationDesc=stationDesc, sectionCode=sectionCode, sectionDesc=sectionDesc, lineCode=lineCode, 
						lineName=lineName, tester=tester, test_time=test_time, testResult=testResult, ResultType=ResultType, errorCode=errorCode, errorDesc=errorDesc,
						testdata=testdata, testFileName=testFileName, testFileByte=testFileByte)
        print "MES response: " + str(response)
        return response
        
    except Exception,e:
        print "Entered into the exception, it's going to close the system"
        print "==================================================================="
        print "SN: ", sn, " with type: ", type(sn)
        print "stationCode: ", stationCode, " with type: ", type(stationCode)
        print "stationDesc: ", stationDesc, " with type: ", type(stationDesc)
        print "sectionCode: ", sectionCode, " with type: ", type(sectionCode)
        print "sectionDesc: ", sectionDesc, " with type: ", type(sectionDesc)
        print "lineCode: ", lineCode, " with type: ", type(lineCode)
        print "lineName: ", lineName, " with type: ", type(lineName)
        print "tester: ", tester, " with type: ", type(tester)
        print "test_time: ", test_time, " with type: ", type(test_time)
        print "testResult: ", testResult, " with type: ", type(testResult)
        print "ResultType: ", ResultType, " with type: ", type(ResultType)
        print "errorCode: ", errorCode, " with type: ", type(errorCode)
        print "errorDesc: ", errorDesc, " with type: ", type(errorDesc)
        print "testdata: ", testdata, " with type: ", type(testdata)
        print "testFileName: ", testFileName, " with type: ", type(testFileName)
        print "testFileByte: ", testFileByte, " with type: ", type(testFileByte)
        print "==================================================================="
        return -1