'''
Created on 11-06-2013

@author: Trung Huynh, Loc Bui
Reference: http://zone.ni.com/reference/en-XX/help/370471W-01/
'''


from numpy import int32, uint32, float64, zeros
from PyDAQmx import *
from PyDAQmx.DAQmxConstants import *
from PyDAQmx.DAQmxTypes import *

import sys


# CONSTANTS
DIGITAL_WRITE_TIMEOUT_IN_SEC = 10.0
DIGITAL_READ_TIMEOUT_IN_SEC = 10.0
ANALOG_WRITE_TIMEOUT_IN_SEC = 10.0
ANALOG_READ_TIMEOUT_IN_SEC = 10.0
ANALOG_MIN_VOL_VAL = 0.0
ANALOG_MAX_VOL_VAL = 5.0


def setDigitalOutput(port, value):
#     if port not in ('Dev1/port0', 'Dev1/port1'):
#         # Error
#         return -1

    if value < 0x00 or value > 0xFF:
        # Error: out of 8 bits range
        return -1

#     DAQmxResetDevice('Dev1')
    task_handle = TaskHandle(0)
    data = numpy.zeros((1,), dtype=uint32) + value
    written = int32()

    # Configure code
    DAQmxCreateTask('SetDigitalOutput', byref(task_handle))
    DAQmxCreateDOChan(task_handle, # taskHandle
                      port, # lines
                      '', # nameToAssignToLines
                      DAQmx_Val_ChanForAllLines) # lineGrouping

    # Start code
    DAQmxStartTask(task_handle)

    # Write Code
    DAQmxWriteDigitalU32(task_handle, # taskHandle
                         1, # numSampsPerChan1
                         1, # autoStart
                         DIGITAL_WRITE_TIMEOUT_IN_SEC, # timeout
                         DAQmx_Val_GroupByChannel, # dataLayout
                         data, # writeArray
                         byref(written), # sampsPerChanWritten
                         None) # reserved

    DAQmxStopTask(task_handle)
    DAQmxClearTask(task_handle)
    return 0

def captureDigitalInput(port, number_of_samples):
#     if port not in ('Dev1/port0', 'Dev1/port1'):
#         # Error
#         return -1

#     DAQmxResetDevice('Dev1')
    task_handle = TaskHandle(0)
    data = numpy.zeros((number_of_samples,), dtype=numpy.uint32)
    read = int32()

    # Configure code
    DAQmxCreateTask('CaptureDigitalInput', byref(task_handle))
    DAQmxCreateDIChan(task_handle, # taskHandle
                      port, # lines
                      '', # nameToAssignToLines
                      DAQmx_Val_ChanForAllLines) # lineGrouping

    # Start code
    DAQmxStartTask(task_handle)

    # Read Code
    DAQmxReadDigitalU32(task_handle, # taskHandle
                        -1, # numSampsPerChan
                        DAQmx_Val_WaitInfinitely, # timeout
                        DAQmx_Val_GroupByChannel, # fillMode
                        data, # readArray
                        number_of_samples, # arraySizeInSamps
                        byref(read), # sampsPerChanRead
                        None) # reserved

#     if read > 0:
#         print 'data: {}, read: {}'.format(data, read)

    DAQmxStopTask(task_handle)
    DAQmxClearTask(task_handle)
    return data


def setAnalogOutput(port, voltage_value):
#     if port not in ('Dev1/ao0', 'Dev1/ao1'):
#          Error
#         return -1

#     DAQmxResetDevice('Dev1')
    task_handle = TaskHandle(0)
    data = numpy.zeros((1,), dtype=float64) + voltage_value

    # Configure code
    DAQmxCreateTask('SetAnalogOutput', byref(task_handle))
    DAQmxCreateAOVoltageChan(task_handle, # taskHandle
                             port, # physicalChannel
                             '', # nameToAssignToChannel
                             ANALOG_MIN_VOL_VAL, # minVal
                             ANALOG_MAX_VOL_VAL, # maxVal
                             DAQmx_Val_Volts, # units
                             '') # customScaleName

    # Start code
    DAQmxStartTask(task_handle)

    # Write Code
    DAQmxWriteAnalogF64(task_handle, # taskHandle
                        1, # numSampsPerChan
                        1, # autoStart
                        ANALOG_WRITE_TIMEOUT_IN_SEC, # timeout
                        DAQmx_Val_GroupByChannel, # dataLayout
                        data, # writeArray
                        None, # sampsPerChanWritten
                        None) # reserved

    DAQmxStopTask(task_handle)
    DAQmxClearTask(task_handle)
    return 0

def captureAnalogInput(port, number_of_samples, rate):
#     if port not in ('Dev1/ai0', 'Dev1/ai1', 'Dev1/ai2', 'Dev1/ai3', 'Dev1/ai4', 'Dev1/ai5', 'Dev1/ai6', 'Dev1/ai7'):
#         # Error
#         return -1

#     DAQmxResetDevice('Dev1')
    task_handle = TaskHandle(0)
    data = zeros((number_of_samples,), dtype=float64)
    read = int32();

    # Configure code
    DAQmxCreateTask('CaptureAnalogInput', byref(task_handle))
    DAQmxCreateAIVoltageChan(task_handle, # taskHandle
                             port, # physicalChannel
                             '', # nameToAssignToChannel
                             DAQmx_Val_RSE, # terminalConfig
                             ANALOG_MIN_VOL_VAL, # minVal
                             ANALOG_MAX_VOL_VAL, # maxVal
                             DAQmx_Val_Volts, # units
                             None) # customScaleName
    DAQmxCfgSampClkTiming(task_handle, # taskHandle
                          '', # source
                          rate, # rate
                          DAQmx_Val_Rising, # activeEdge
                          DAQmx_Val_FiniteSamps, # sampleMode
                          number_of_samples) # sampsPerChanToAcquire

    # Start code
    DAQmxStartTask(task_handle)

    # Read Code
    DAQmxReadAnalogF64(task_handle, # taskHandle
                       -1, # numSampsPerChan
                       ANALOG_READ_TIMEOUT_IN_SEC, # timeout
                       DAQmx_Val_GroupByChannel, # fillMode
                       data, #readArray
                       number_of_samples, # arraySizeInSamps
                       byref(read), # sampsPerChanRead
                       None) # reserved

#     if read > 0:
#         print 'data: {}, read: {}'.format(data, read)

    DAQmxStopTask(task_handle)
    DAQmxClearTask(task_handle)
    return data

'''
def main(options):
    setDigitalOutput('Dev1/port0', 0x1F)
    captureDigitalInput('Dev1/port0', 1)
    setAnalogOutput('Dev1/ao0', 1.0)
    captureAnalogInput('Dev1/ai0', 10, 10000.0)

if __name__ == '__main__':
    main(sys.argv[1:])
'''
