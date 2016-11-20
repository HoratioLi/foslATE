#!/usr/bin/env python
'''
Created on 2014-07-16

@author: Rachel Kalmar
'''

from constants import *
from helper.utils import *

params = {}

params['device_type'] = DEVICE_TYPE
params['debug_mode'] = DEBUG_MODE
params['verbose_mode'] = VERBOSE_MODE
params['stop_after_fail'] = STOP_AFTER_FAIL
params['num_readings'] = NUM_READINGS
params['num_readings_baseline'] = NUM_READINGS_BASELINE
params['baseline_window_size'] = BASELINE_WINDOW_SIZE
params['serial_timeout'] = SERIAL_TIMEOUT
params['testIndex'] = 0
params['numTests'] = 0
params['img_file_path'] = IMAGE_FILE_PATH
params['isRunningOnPi'] = IS_RUNNING_ON_PI
params['default_current_range'] = DEFAULT_CURRENT_RANGE
params['pi_voltage_lower'] = PI_VOLTAGE_LOWER
params['pi_voltage_upper'] = PI_VOLTAGE_UPPER
params['git_commit_hash'] = get_git_revision_hash()
# params['programming_done'] = True

if DEVICE_TYPE == 'Venus':
    params['mcu_current_lower'] = VENUS_MCU_CURRENT_LOWER
    params['mcu_current_upper'] = VENUS_MCU_CURRENT_UPPER
    params['idle_current_lower'] = VENUS_IDLE_CURRENT_LOWER
    params['idle_current_upper'] = VENUS_IDLE_CURRENT_UPPER    
    params['led_current_lower'] = VENUS_LED_CURRENT_LOWER
    params['led_current_upper'] = VENUS_LED_CURRENT_UPPER        
    params['load_current_lower'] = VENUS_LOAD_CURRENT_LOWER
    params['load_current_upper'] = VENUS_LOAD_CURRENT_UPPER  
    params['accel_current_lower'] = VENUS_ACCEL_CURRENT_LOWER
    params['accel_current_upper'] = VENUS_ACCEL_CURRENT_UPPER  
    params['deep_sleep_current_lower'] = VENUS_DEEP_SLEEP_CURRENT_LOWER
    params['deep_sleep_current_upper'] = VENUS_DEEP_SLEEP_CURRENT_UPPER 
    params['z_data_threshold_lower'] = VENUS_Z_DATA_THRESHOLD_LOWER
    params['z_data_threshold_upper'] = VENUS_Z_DATA_THRESHOLD_UPPER   
    params['oper_curr_thresh_upper'] = VENUS_OPER_CURR_THRESH_UPPER
    params['oper_curr_thresh_lower'] = VENUS_OPER_CURR_THRESH_LOWER
    params['batt_base_voltage_lower'] = VENUS_BATT_BASE_VOLTAGE_THRESH_LOWER
    params['batt_base_voltage_upper'] = VENUS_BATT_BASE_VOLTAGE_THRESH_UPPER
    params['batt_load_voltage_lower'] = VENUS_BATT_LOAD_VOLTAGE_THRESH_LOWER
    params['batt_load_voltage_upper'] = VENUS_BATT_LOAD_VOLTAGE_THRESH_UPPER    
    params['rssi_lower'] = VENUS_RSSI_LOWER
    params['rssi_upper'] = VENUS_RSSI_UPPER
    params['baud_rate'] = VENUS_SERIAL_BAUDRATE
elif DEVICE_TYPE == 'Apollo':
    params['mcu_current_lower'] = APOLLO_MCU_CURRENT_LOWER
    params['mcu_current_upper'] = APOLLO_MCU_CURRENT_UPPER
    params['idle_current_lower'] = APOLLO_IDLE_CURRENT_LOWER
    params['idle_current_upper'] = APOLLO_IDLE_CURRENT_UPPER    
    params['led_current_lower'] = APOLLO_LED_CURRENT_LOWER
    params['led_current_upper'] = APOLLO_LED_CURRENT_UPPER        
    params['load_current_lower'] = APOLLO_LOAD_CURRENT_LOWER
    params['load_current_upper'] = APOLLO_LOAD_CURRENT_UPPER  
    params['accel_current_lower'] = APOLLO_ACCEL_CURRENT_LOWER
    params['accel_current_upper'] = APOLLO_ACCEL_CURRENT_UPPER  
    params['deep_sleep_current_lower'] = APOLLO_DEEP_SLEEP_CURRENT_LOWER
    params['deep_sleep_current_upper'] = APOLLO_DEEP_SLEEP_CURRENT_UPPER 
    params['z_data_threshold_lower'] = APOLLO_Z_DATA_THRESHOLD_LOWER
    params['z_data_threshold_upper'] = APOLLO_Z_DATA_THRESHOLD_UPPER
    params['oper_curr_thresh_upper'] = APOLLO_OPER_CURR_THRESH_UPPER
    params['oper_curr_thresh_lower'] = APOLLO_OPER_CURR_THRESH_LOWER    
    params['batt_base_voltage_lower'] = APOLLO_BATT_BASE_VOLTAGE_THRESH_LOWER
    params['batt_base_voltage_upper'] = APOLLO_BATT_BASE_VOLTAGE_THRESH_UPPER
    params['batt_load_voltage_lower'] = APOLLO_BATT_LOAD_VOLTAGE_THRESH_LOWER
    params['batt_load_voltage_upper'] = APOLLO_BATT_LOAD_VOLTAGE_THRESH_UPPER        
    params['rssi_lower'] = APOLLO_RSSI_LOWER
    params['rssi_upper'] = APOLLO_RSSI_UPPER
    params['baud_rate'] = APOLLO_SERIAL_BAUDRATE  

