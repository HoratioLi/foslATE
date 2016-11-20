#!/usr/bin/env python

'''
Utils for extracting information from PostgreSQL

Created on Nov 10, 2013

@author: 
'''


import sys

from operator import itemgetter, attrgetter
#import misfitutils as mfu
#from helper import util as mfu
import psycopg2

from datetime import datetime, timedelta
import calendar
import time

import numpy as np
import matplotlib.pylab as plt
import matplotlib.legend
from matplotlib.widgets import Button
import math
from view.batteryStartGui import startGui

HWLOG_COL = 0
SN_COL = 1
DATE_COL = 2
TIMESTAMP_COL = 3
EMAIL_COL = 4

USAGE_TEXT = """
USAGE: python postgresDB_extractor.py shine_prod|shine_staging email|serial_number <email/serial_number> <startDate> <endDate>
"""
plot_passed = False
button_hit = False


def connectToDB(database):
    con = None

    try:
         
        con = psycopg2.connect(database=database, host = 'localhost', port = '5433', user = 'dbr', password = 'Bf8gfAmg') 
        cur = con.cursor()
        cur.execute('SELECT version()')          
        ver = cur.fetchone()
        print ver    
        print 'Connect to DB Done!'
        return cur

    except psycopg2.DatabaseError, e:
        print 'Error %s' % e    
        sys.exit(1)

        
def closeDB(cur):
    cur.close()


'''

- battery_data: array of [prior_sync_time, current_sync_time, array of [entry_timestamp, tz_offset, base_vol, load_vol, bat_temp, rep_bat_lev, cal_bat_lev]]
'''
def prepareBatteryInfoToPlot(battery_data):
    x_ = [] # timestamp made up for correctness
    x = [] # timestamp read from log entry
    y1 = [] # tz_offset
    y2 = [] # base_vol
    y3 = [] # load_vol
    y4 = [] # bat_temp
    y5 = [] # rep_bat_lev
    y6 = [] # cal_bat_lev

    for batt_sync in battery_data:
        prior_sync_time = batt_sync[0]
        current_sync_time = batt_sync[1]
        batt_entries = batt_sync[2]
        num_entries = len(batt_entries)

        if prior_sync_time == None:
            t = datetime.utcfromtimestamp(float(current_sync_time) - 3*60*60)
            b = batt_entries[num_entries-1]
            print '{}, {}'.format(t,b)
            x_.append(t)
            x.append(b[0])
            y1.append(b[1])
            y2.append(b[2])
            y3.append(b[3])
            y4.append(b[4])
            y5.append(b[5])
            y6.append(b[6])
        else:
            print '--- \n{}'.format(datetime.utcfromtimestamp(float(prior_sync_time)))
            
            #duration = (current_sync_time - prior_sync_time)/num_entries
            duration = 3*60*60
            entry_time = prior_sync_time
            if (current_sync_time - prior_sync_time) > (num_entries + 1) * duration:
                entry_time = current_sync_time - num_entries*duration
           
            for b in batt_entries:
                #b: [timestamp, tz_offset, base_vol, load_vol, bat_temp, rep_bat_lev, cal_bat_lev]
                t = datetime.utcfromtimestamp(float(entry_time))
                print '{}, {}'.format(t, b)
                x_.append(t)
                x.append(b[0])
                y1.append(b[1])
                y2.append(b[2])
                y3.append(b[3])
                y4.append(b[4])
                y5.append(b[5])
                y6.append(b[6])   
                entry_time = entry_time + duration

            print datetime.utcfromtimestamp(float(current_sync_time))
                
    return [x_, x, y1, y2, y3, y4, y5, y6] 



def getLogData(cursor, email, sDate, eDate):
    print '\nGetting sync log data...'
    query = '''
        SELECT * FROM sync_log_file slf
        WHERE slf.email like '{}'
        AND basename = 'hardware_log'
        AND slf.date >= '{}'
        AND slf.date <= '{}';'''.format(email, sDate, eDate);
    #print query
    cursor.execute(query);
    print 'Done!'
    result = []
    row = cursor.fetchone()
    while row:
        #print '{}, {}, {}: \n {}'.format(row[3], row[5], row[7], row[8])
        for eachlogentry in parseHwLogStr(row[8]):
            print eachlogentry
            result.append(eachlogentry)
        row = cursor.fetchone()

    #mfu.printPrettyHwLogList(result)
    
def getEntryBatteryData(cursor, sDate, eDate):
    print '\nGetting sync log data...'
    query = '''
        SELECT * FROM sync_log_file slf
        WHERE basename = 'hardware_log'
        AND slf.date >= '{}'
        AND slf.date <= '{}';'''.format( sDate, eDate);
    # print query
    cursor.execute(query);
    print 'Done!'
    result = []
    row = cursor.fetchone()
    while row:
        # row: 0. sync_log_file_id, 1.key, 2.dirname, 3.basename, 4.date, 5.email, 6.serial_number, 7.sync_start, 8. content
        # print '{}, {}, {}: \n {}'.format(row[3], row[5], row[7], row[8])
        i = 0

        row8 = row[8].split(',')
        for eachrow in row8:
            for eachlogentry in getBatteryFromHwLogStr(eachrow):
                print '{}: {}'.format(i,eachlogentry)
                result.append(eachlogentry)
                i = i + 1
        row = cursor.fetchone()
        print '-------------'

    printPrettyBatteryInfoList(result)


def getEntryBatteryDataByEmail(cursor, email, sDate, eDate):
    print '\nGetting sync log data...'
  
    query = '''
        SELECT * FROM sync_log_file slf
        WHERE slf.email like '{}'
        AND basename = 'hardware_log'
        AND slf.date >= '{}'
        AND slf.date <= '{}'
        ORDER BY slf.sync_start;'''.format(email, sDate, eDate);
    
    #print query
    cursor.execute(query);
    print 'Done!'
    result = []
    row = cursor.fetchone()
    prior_sync_time = None 
    while row:
        # row: 0. sync_log_file_id, 1.key, 2.dirname, 3.basename, 4.date, 5.email, 6.serial_number, 7.sync_start, 8. content
        #print '{}, {}, {}: \n {}'.format(row[3], row[5], row[7], row[8])
        i = 0
        sync_batt_entries = []
        avg_batt_level = 0
        contents = row[8].split(',')
        for content in contents:
            for eachBattEntry in getBatteryFromHwLogStr(content):
                # eachBattEntry: [timestamp, tz_offset, base_vol, load_vol, bat_temp, rep_bat_lev, cal_bat_lev]
                print '{}: {}'.format(i,eachBattEntry)
                #result.append(eachBattEntry)
                avg_batt_level = avg_batt_level + eachBattEntry[5]
                sync_batt_entries.append(eachBattEntry)           
                i = i + 1

        if i != 0:
            avg_batt_level = avg_batt_level/i
            result.append([prior_sync_time, row[7], sync_batt_entries])
        prior_sync_time = row[7]
        row = cursor.fetchone()
        #print '-------------'

    # result1 = np.array(result)
    # print result1[:,0]
    # print result1.transpose()
    # printPrettyBatteryInfoList(result)  
    return result  


def getSyncBatteryDataByEmail(cursor, email, sDate, eDate):
    print '\nGetting sync log data...'
    
    t = datetime.now()

    query = '''
        SELECT * FROM sync_log_file slf
        WHERE slf.email like '{}'
        AND basename = 'hardware_log'
        AND slf.date >= '{}'
        AND slf.date <= '{}'
        ORDER BY slf.sync_start;'''.format(email, sDate, eDate);
    
    # print query
    cursor.execute(query);
    print 'Done!'
    t = datetime.now() - t
    print 'Querying time: {}'.format(t)
    t = datetime.now()
    result = []
    row = cursor.fetchone()
    while row:
        # row: 0. sync_log_file_id, 1.key, 2.dirname, 3.basename, 4.date, 5.email, 6.serial_number, 7.sync_start, 8. content
        # print '{}, {}, {}: \n {}'.format(row[3], row[5], row[7], row[8])
        i = 0
        avg_batt_level = 0
        contents = row[8].split(',')
        for content in contents:
            for eachBattEntry in getBatteryFromHwLogStr(content):
                # eachBattEntry: [timestamp, tz_offset, base_vol, load_vol, bat_temp, rep_bat_lev, cal_bat_lev]
                # print '{}: {}'.format(i,eachBattEntry)
                #result.append(eachBattEntry)
                avg_batt_level = avg_batt_level + eachBattEntry[5]
                i = i + 1
        if i != 0:
            avg_batt_level = avg_batt_level/i
            result.append([datetime.utcfromtimestamp(float(row[7])), row[7], avg_batt_level])
        row = cursor.fetchone()
        #print '-------------'

    result1 = np.array(result)
    # print result1[:,0]
    # print result1.transpose()
    # printPrettyBatteryInfoList(result)  
    t = datetime.now() - t
    print 'Time to process data: {}'.format(t)
    return result  

def getSyncBatteryData(cursor, num, sDate, eDate):
    print '\nGetting sync log data...'
    
    #query = '''
    #    SELECT * FROM sync_log_file slf
    #    WHERE slf.email like '{}'
    #    AND basename = 'hardware_log'
    #    AND slf.date >= '{}'
    #    AND slf.date <= '{}'
    #    ORDER BY slf.sync_start;'''.format(email, sDate, eDate);
    
    query = '''
        SELECT * FROM sync_log_file slf
        WHERE basename = 'hardware_log'
        AND slf.date >= '{}'
        AND slf.date <= '{}'
        ORDER BY slf.sync_start;'''.format( sDate, eDate);
    
    # print query
    cursor.execute(query);
    print 'Done!'
    result = []
    row = cursor.fetchone()
    while row:
        # row: 0. sync_log_file_id, 1.key, 2.dirname, 3.basename, 4.date, 5.email, 6.serial_number, 7.sync_start, 8. content
        # print '{}, {}, {}: \n {}'.format(row[3], row[5], row[7], row[8])
        i = 0
        avg_batt_level = 0
        row8 = row[8].split(',')
        for eachrow in row8:
            for eachlogentry in getBatteryFromHwLogStr(eachrow):
                # print '{}: {}'.format(i,eachlogentry)
                #result.append(eachlogentry)
                avg_batt_level = avg_batt_level + eachlogentry[5]
                i = i + 1
        if i != 0:
            avg_batt_level = avg_batt_level/i
            result.append([datetime.utcfromtimestamp(float(row[7])), row[7], avg_batt_level])
        row = cursor.fetchone()
        #print '-------------'

    result1 = np.array(result)
    # print result1[:,0]
    # print result1.transpose()
    # printPrettyBatteryInfoList(result)  
    return result  
    
def plotSyncBattery(result):

    #print x
    #print y
    #print x_ticks
    time = []
    batt_level = []

    for eachrow in result:
        time.append(eachrow[0])
        #time.append(datetime.utcfromtimestamp(float(eachrow[1])))
        batt_level.append(eachrow[2])

    fig = plt.figure()
    fig.suptitle('\nBattery Level')

    ax1 = fig.add_subplot(111)
    ax1.plot(time, batt_level)
    ax1.hold
    ax1.scatter(time, batt_level)
    #ax1.bar(x, y, color='blue', align='center', width = 400)
    #for x,y in zip(col0[8:], col1[8:]):
    #    ax1.text(x, y + 25, '(%.0d)' % y, ha='center', va= 'bottom')

    ax1.set_xlabel('Time') # start_plot_t.isoformat(' '))
    ax1.set_ylabel('Battery Level')
    #plt.ylim(0,22000)
    #plt.xlim(0, 40000)
    plt.grid(True)
    plt.xticks(rotation=30)
    #plt.xticks((x[0], x[len(x)-1]), (x_ticks[0], x_ticks[len(x)-1]), rotation = 20)

    #ax12 = ax1.twinx()
    #rsl = csu.sr2rsl(step, c)
    #distpermin = height * rsl * step / 63360
    #dist = np.cumsum(distpermin)
    #ax12.plot(t, dist, color='r', linewidth=3.0)
    #ax12.set_ylabel('distance (mile)')
    #plt.xlim([start_plot,end_plot])

    plt.show()
    fig.savefig("batt_level.png",dpi=400)

def plotEntryBattery(data, email):
    
    #num_rows = data.shape[0]
    #num_cols = data.shape[1]
    
    #[timestamp, tz_offset, base_vol, load_vol, bat_temp, rep_bat_lev, cal_bat_lev]
    time = data[0]
    timestamp = data[1]
    tz_offset = data[2]
    base_vol = data[3]
    load_vol = data[4]
    bat_temp = data[5]
    rep_bat_lev = data[6]
    cal_bat_lev = data[7]
    
    #print qttype[1] 

    # for i in (0,1,2,3,4):
    #     col = data[:,i]
    #     fig = plt.figure()
    #     fig.suptitle('Histogram of in-entry number of {}quad_tap\n(first entry excluded)'.format(qttype[i]))

    #     ax1 = fig.add_subplot(111)
    #     ax1.hist(col, 60, log=True)

    #     ax1.set_xlabel('Number of {}quad_tap'.format(qttype[i])) # start_plot_t.isoformat(' '))
    #     ax1.set_ylabel('Count')
    #     #plt.ylim(0,22000)
    #     plt.xlim(0,200)
    #     plt.grid(True)
    #     #plt.xticks(ticks)

    #     #plt.show()
    #     fig.savefig('hist_{}{}.png'.format(qttype[i],file_name),dpi=400)

    fig = plt.figure()
    fig.suptitle('')

        
    ax1 = fig.add_subplot(4,1,1)
    ax1.plot(time, rep_bat_lev, 'o-')
    ax1.set_xlabel('Time') # start_plot_t.isoformat(' '))
    ax1.set_ylabel('Battery Level')
    plt.grid(True)
    
    ax1 = fig.add_subplot(4,1,2)
    ax1.plot(time, bat_temp, 'o-')
    ax1.set_xlabel('Time') # start_plot_t.isoformat(' '))
    ax1.set_ylabel('Battery Temp')
    plt.grid(True)
        
    ax1 = fig.add_subplot(4,1,3)
    ax1.plot(time, base_vol, 'o-')
    ax1.set_xlabel('Time') # start_plot_t.isoformat(' '))
    ax1.set_ylabel('Base Voltage')
    plt.grid(True)
    
    ax1 = fig.add_subplot(4,1,4)
    ax1.plot(time, load_vol, 'o-')
    ax1.set_xlabel('Time') # start_plot_t.isoformat(' '))
    ax1.set_ylabel('Load Voltage')

    #plt.ylim(0,22000)
    #plt.xlim(0,200)
    plt.grid(True)
    #plt.xticks(ticks)

    plt.show()
    fig.savefig('{}.png'.format(email),dpi=400)
 

def getHistogramUsersByFirmware(cursor, firmware):
    print '\nGetting data from database...'
    
    t = datetime.now()

    query = '''
select date_trunc('day', sync_end), count(distinct email)
from user_raw_data
where firmware = '{}'
group by date_trunc('day', sync_end)
order by date_trunc('day', sync_end);
'''.format(firmware);
    
    # print query
    cursor.execute(query);
    print 'Done!'
    t = datetime.now() - t
    print 'Querying time: {}'.format(t)
    t = datetime.now()

    x = []
    y = []
    row = cursor.fetchone()
    while row:
        if row[1] > 100:
            x.append(row[0])
            y.append(row[1])
        row = cursor.fetchone()
    
    return (x,y)

def plotHistogramUsersByFirmware(firmware, time, count, hold):
    fig = plt.figure()
    fig.suptitle('\nNumber of Users by Date for firmware \'{}\''.format(firmware))

    ax1 = fig.add_subplot(111)
    
    ax1.bar(time, count, color='blue', align='center')
    for x,y in zip(time, count):
        if y < 100:
            ax1.text(x, y + 25, '(%.0d)' % y, ha='center', va= 'bottom')

    ax1.set_xlabel('Date') # start_plot_t.isoformat(' '))
    ax1.set_ylabel('#Users')
    #plt.ylim(0,22000)
    #plt.xlim(0, 40000)
    plt.grid(True)
    plt.xticks(rotation=30)
    #plt.xticks((x[0], x[len(x)-1]), (x_ticks[0], x_ticks[len(x)-1]), rotation = 20)
    fig.savefig('hist_users_date_{}.png'.format(firmware),dpi=400)


def getNumUserByDateFirmware(cursor):
    print '\nGetting data from database...'
    
    t = datetime.now()

    query = '''
select date_trunc('day', sync_end),
    count(case when firmware = '0.0.31r' then 1 else null end) ,
    count(case when firmware = '0.0.35r' then 1 else null end) ,
    count(case when firmware = '0.0.37r' then 1 else null end) ,
    count(case when firmware = '0.0.43r' then 1 else null end) ,
    count(case when firmware = '0.0.50r' then 1 else null end) s
from user_raw_data
--where firmware in ('0.0.50r','0.0.43r','0.0.37r','0.0.35r','0.0.31r','0.0.29r','0.0.28x.boot2_prod')
where firmware in ('0.0.51r','0.0.50r','0.0.48r','0.0.43r','0.0.37r','0.0.35r','0.0.31r','0.0.29r','0.0.28x.boot2_prod')
and sync_end > '2013-08-01' and sync_end < now() 
group by date_trunc('day', sync_end) 
;
''';
    
    # print query
    cursor.execute(query);
    print 'Done!'
    t = datetime.now() - t
    print 'Querying time: {}'.format(t)
    t = datetime.now()

    x = []
    y1 = []
    y2 = []
    y3 = []
    y4 = []
    y5 = []
    row = cursor.fetchone()
    while row:
        x.append(row[0])
        y1.append(row[1])
        y2.append(row[2])
        y3.append(row[3])
        y4.append(row[4])
        y5.append(row[5])
        row = cursor.fetchone()
    
    return (x,y1, y2, y3, y4,y5)

def plotNumUserByDateFirmware(x, y1, y2, y3, y4, y5):
    fig = plt.figure(figsize=(8, 6))
    fig.suptitle('\nNumber of Syncs by Date and Firmware')

    ax1 = fig.add_subplot(111)
    
    p1=ax1.plot(x,y1, 'co-', label = '31r')
    p1=ax1.plot(x,y2, 'yo-', label = '35r')
    p2=ax1.plot(x,y3, 'go-', label = '37r')
    p3=ax1.plot(x,y4, 'bo-', label = '43r')
    p4=ax1.plot(x,y5, 'ro-', label = '50r')
    
    ax1.legend(loc='upper left', shadow=True)

    ax1.set_xlabel('Date') # start_plot_t.isoformat(' '))
    ax1.set_ylabel('#Syncs')
    #plt.ylim(0,22000)
    #plt.xlim(0, 40000)
    plt.grid(True)
    #plt.xticks(rotation=30)
    #plt.xticks((x[0], x[len(x)-1]), (x_ticks[0], x_ticks[len(x)-1]), rotation = 20)
    fig.savefig('sync_firmware_tracking.png',dpi=400)

def getBatteryWithResetData(database, inputType, input, sDate, eDate):
    if inputType != 'email' and inputType != 'serial_number':
        print 'Input type must be email or serial_number'
        return []

    cursor = connectToDB(database)
    print '\nGetting battery logs from database...'
    
    t = datetime.now()

# ---- Get metadata 
#     query = '''
# select sync_end, count(1)
# from hardware_log hw inner join user_raw_data urd on (hw.user_raw_data_id = urd.user_raw_data_id)
# where {} = '{}'
# and sync_end >= '{}'
# and sync_end <= '{}'
# and (primary_code = 242 or primary_code = 4)
# group by sync_end
# order by sync_end;
# '''.format(inputType, input, sDate, eDate);

#     cursor.execute(query);
    
#     prior_sync_time = None
#     metadata = [] # each element contain [prior_sync_time, current_sync_time, #entries]
#     row = cursor.fetchone();
#     while row:
#         metadata.append([prior_sync_time, row[0], row[1]])
#         print '{},{},{}'.format(prior_sync_time, row[0], row[1])
#         prior_sync_time = row[0]
#         row = cursor.fetchone();
        
    
# ----then get real data



    query = '''
select 
    hw.event_timestamp entry_timestamp, 
    urd.sync_end sync_time, 
    event_index entry_index, 
    hw.tz_offset,
    primary_code, 
    hw.data -> 'type' entry_type, 
    hw.data -> 'reset_cause' reset_cause, 
    (hw.data -> 'base_battery_voltage')::integer base_voltage, 
    (hw.data -> 'load_battery_voltage')::integer load_voltage, 
    (hw.data -> 'battery_temperature')::integer battery_temperature, 
    (hw.data -> 'reported_battery_level')::integer reported_battery_level, 
    (hw.data -> 'calculated_battery_level')::integer calculated_battery_level, 
    firmware
from hardware_log hw inner join user_raw_data urd on (hw.user_raw_data_id = urd.user_raw_data_id)
where {} = '{}'
and sync_end >= '{}'
and sync_end <= '{}'
and (primary_code = 242 or primary_code = 4)
order by sync_end, hw.event_index;
'''.format(inputType, input, sDate, eDate);
    
    
    print query
    cursor.execute(query);
    print 'Done!'
    t = datetime.now() - t
    print 'Querying time: {}'.format(t)
   
    x_ = [] # 'corrected' timestamp for battery display
    x = [] # timestamp (read from db) for battery display
    y0 = [] # tz_offset
    y1 = [] # firmware
    y2 = [] # base_vol
    y3 = [] # load_vol
    y4 = [] # bat_temp
    y5 = [] # rep_bat_lev
    y6 = [] # cal_bat_lev
    
    rx_ = [] # 'corrected' timestamp for reset info display
    rx = [] # timestamp (read from db) for reset info display
    ry0 = [] # tz_offset for reset
    ry1 = [] # firmware
    ry2 = [] # reset cause

    dump = []
    timedata = []
    
    prior_sync_time = None
    current_sync_time = None
    is_reset = False
    firmware = None
    a_sync_timedata = []
   
    row = cursor.fetchone()
    while row:
        if row[4] == 242: # battery info
            x.append(row[0])
            y0.append(row[3])
            y1.append(row[12])
            y2.append(row[7])
            y3.append(row[8])
            y4.append(row[9])
            y5.append(row[10])
            y6.append(row[11])
        elif row[4] == 4: # reset info
            rx.append(row[0])
            ry0.append(row[3])
            ry1.append(row[12])
            ry2.append(row[6])

        # prepare for correcting timestamp
        t = calendar.timegm(row[0].timetuple()) # convert entry time to epoch time           
        t1 = calendar.timegm(row[1].timetuple()) # convert sync time to epoch time
        if t1 == current_sync_time:
            a_sync_timedata.append([row[4],t])
        else:
            if current_sync_time != None:
                timedata.append([prior_sync_time, current_sync_time, is_reset, a_sync_timedata, firmware])
            prior_sync_time = current_sync_time
            current_sync_time = t1
            is_reset = False
            a_sync_timedata = [[row[4],t]]

        firmware = row[12]
        if is_reset == False and (t < 1372662000 or t > time.time()):
            #print 'is reset'
            is_reset = True

        if current_sync_time != None:
            print '=== current_sync_time = {}, row_sync_time = {}, row_entry_time = {}, < 1372662000: {}, , is_reset = {}'.format(datetime.utcfromtimestamp(float(current_sync_time)),row[1], row[0], t < 1372662000, is_reset)
     
        dump.append(row)
        row = cursor.fetchone()

    ### done with DB - close it.
    closeDB(cursor)

    # add last sync 
    if current_sync_time != None:
        timedata.append([prior_sync_time, current_sync_time, is_reset, a_sync_timedata, firmware])
    
    i = 0
    # ---- correcting timestamp for both battery entries and reset entries
    for atimedata in timedata:
        prior_sync_time = atimedata[0]
        current_sync_time = atimedata[1]
        is_reset = atimedata[2]
        a_sync_timedata = atimedata[3]
        num_entries = len(a_sync_timedata)
        firmware = atimedata[4]

        if prior_sync_time == None:
            prior_sync_time = current_sync_time - 4*60*60
        
        print '--- \nPrior sync time: {}'.format(datetime.utcfromtimestamp(float(prior_sync_time)))
        
        # firmware 50r and later: duration is 3 hours apart
        duration = 3*60*60
        if firmware < '0.0.50r':
            duration = 4*60*60
        if (current_sync_time - prior_sync_time) < num_entries * duration:
            duration = (current_sync_time - prior_sync_time) / num_entries
        
        entry_time = prior_sync_time - duration
        if (current_sync_time - prior_sync_time) > num_entries * duration:
            #print 'Test'
            entry_time = current_sync_time - (num_entries+1) * duration
        
        for entry in a_sync_timedata:                

            if is_reset == False:
                entry_time = entry[1]
                #entry_time = (int) t
            else:
                entry_time = entry_time + duration
            
            if entry[0] == 242:
                x_.append(entry_time)
            elif entry[0] == 4:
                rx_.append(entry_time)

            #dump[i].insert(0,datetime.utcfromtimestamp(float(entry_time)))
            print dump[i]
            i = i + 1
            print '{}, {}, {}'.format(entry_time, datetime.utcfromtimestamp(float(entry_time)),datetime.utcfromtimestamp(float(entry[1])))
           
        print 'is_reset = {}\nCurrent sync time: {}'.format(is_reset,datetime.utcfromtimestamp(float(current_sync_time)))

    # return (battery_info, reset_info) --> need to create models for these
    return ({'time_corrected':x_, 'time':x, 'tz_offset': y0, 'base_vol':y2, 'load_vol':y3, 'bat_temp':y4, 'rep_bat_lev':y5, 'cal_bat_lev':y6, 'firmware':y1}, {'time_corrected':rx_, 'time':rx, 'tz_offset': ry0, 'firmware':ry1, 'reset_cause':ry2})
    #battery = []
    #reset = []
    #return(baterry, reset)

def getDailyActivity(database, inputType, input, sDate, eDate):
    if inputType != 'email' and inputType != 'serial_number':
        print 'Input type must be email or serial_number'
        return []

    cursor = connectToDB(database)
    print '\nGetting daily activity data from database...'
    
    t = datetime.now()

    query = '''
select 
    record_date,
    step_sum_utc,
    point_sum_utc,
    double_tap_sum_utc,
    triple_tap_sum_utc
from user_daily_data
where {} = '{}'
and record_date >= '{}'
and record_date <= '{}'
order by record_date;
'''.format(inputType, input, sDate, eDate);
    
    # print query
    cursor.execute(query);
    print 'Done!'
    t = datetime.now() - t
    print 'Querying time: {}'.format(t)

    time = []
    
    format = "%Y-%m-%d"
    startD = datetime.strptime(sDate, format)
    endD = datetime.strptime(eDate, format)
    startD = calendar.timegm(startD.timetuple())
    endD = calendar.timegm(endD.timetuple())
    d = startD
    while d <= endD: 
        time.append(d)
        d = d + 24*60*60
    steps = [0] * len(time)
    points = [1] * len(time)
    dtaps = [1] * len(time)
    ttaps = [1] * len(time)
    
    #print convertEpochToDateime(time)
    #print steps
    
    row = cursor.fetchone()
    while row:
        t = calendar.timegm(row[0].timetuple())
        idx =  (int) (t - startD)/(24*60*60)
        time[idx] = t
        steps[idx] = row[1]
        points[idx] = row[2]
        dtaps[idx] = row[3]    
        ttaps[idx] = row[4]
        #print '{}, {}'.format(idx,row)
        row = cursor.fetchone()

    #print time
    #print steps
    closeDB(cursor)

    return {'time':time, 'steps':steps, 'points':points, 'dtaps':dtaps, 'ttaps':ttaps}


def getNumSync(database, inputType, input, sDate, eDate):
    if inputType != 'email' and inputType != 'serial_number':
        print 'Input type must be email or serial_number'
        return []

    cursor = connectToDB(database)
    print '\nGetting sync data from database...'
    
    t = datetime.now()

    format = "%Y-%m-%d"
    # datetime
    startD = datetime.strptime(sDate, format)
    endD = datetime.strptime(eDate, format)
    # epoch time
    startD = calendar.timegm(startD.timetuple())
    endD = calendar.timegm(endD.timetuple())

    query = '''
select date d,
    count(case when basename = 'debug_log.txt' then 1 else null end) num_sync,
    count(case when basename = '0101' then 1 else null end) num_successful_sync
from sync_log_file
where {} = '{}'
    and date >= '{}' 
    and date <= '{}'
group by date
order by date;
'''.format(inputType, input, sDate, eDate);

    
    # print query
    cursor.execute(query);
    print 'Done!'
    t = datetime.now() - t
    print 'Querying time: {}'.format(t)
    
    data = []   

    sync_time = []
    num_sync = []
    num_failed_sync = []
    num_successful_sync = []

    row = cursor.fetchone()
    while row:
        t = calendar.timegm(row[0].timetuple())
        sync_time.append(t)
        num_sync.append(row[1])
        num_failed_sync.append(row[1]-row[2])
        num_successful_sync.append(row[2])
        
        r = {'epochTime':t, 'time': row[0], 'nSync': row[1], 'nFSync':row[1]-row[2], 'nSSync':row[2]}
        data.append(r)
        #print '{}, {}'.format(idx,row)
        row = cursor.fetchone()

    #print time
    #print steps
    closeDB(cursor)

    return (data, {'epochTime':sync_time, 'nSync': num_sync, 'nFSync':num_failed_sync, 'nSSync':num_successful_sync})

def getFirmwareAppVersion(database, inputType, input, sDate, eDate):
    if inputType != 'email' and inputType != 'serial_number':
        print 'Input type must be email or serial_number'
        return []

    cursor = connectToDB(database)
    print '\nGetting firmware from database...'
    
    t = datetime.now()

    format = "%Y-%m-%d"
    # datetime
    startD = datetime.strptime(sDate, format)
    endD = datetime.strptime(eDate, format)
    # epoch time
    startD = calendar.timegm(startD.timetuple())
    endD = calendar.timegm(endD.timetuple())

    query = '''
select firmware, min(sync_end), max(sync_end)
from user_raw_data
where {} = '{}'
    and sync_end >= '{}' 
    and sync_end <= '{}'
group by firmware
order by min(sync_end)
'''.format(inputType, input, sDate, eDate);

    
    # print query
    cursor.execute(query);
    print 'Done!'
    t = datetime.now() - t
    print 'Querying time: {}'.format(t)

    fw = []
    minT = []
    maxT = []
    duration = []
    
    row = cursor.fetchone()
    while row:
        t = calendar.timegm(row[1].timetuple())
        
        if row[0] is None:
            print 'firmware is none'
            row = cursor.fetchone()
            continue
        
        fw.append(row[0])
        minT.append(t)
        t = calendar.timegm(row[2].timetuple())
        maxT.append(t)
        
        row = cursor.fetchone()

    for i in range(len(minT)-1):
        duration.append(minT[i+1] - minT[i])
    duration.append(maxT[len(maxT)-1] - minT[len(minT)-1])

    # App Version
    print '\nGetting app versions from database...'
    t = datetime.now()

    query = '''
select app_version, min(sync_end), max(sync_end)
from user_raw_data
where {} = '{}'
    and sync_end >= '{}' 
    and sync_end <= '{}'
group by app_version
order by min(sync_end)
'''.format(inputType, input, sDate, eDate);

    # print query
    cursor.execute(query);
    print 'Done!'
    t = datetime.now() - t
    print 'Querying time: {}'.format(t)

    app = []
    aMinT = []
    aMaxT = []
    aDuration = []
    
    row = cursor.fetchone()
    while row:
        app.append(row[0])
        t = calendar.timegm(row[1].timetuple())
        aMinT.append(t)
        t = calendar.timegm(row[2].timetuple())
        aMaxT.append(t)
        
        row = cursor.fetchone()

    for i in range(len(aMinT)-1):
        aDuration.append(aMinT[i+1] - aMinT[i])
    aDuration.append(aMaxT[len(aMaxT)-1] - aMinT[len(aMinT)-1])
    closeDB(cursor)

    return ({'firmware':fw, 'start_time':minT, 'duration':duration}, {'app':app, 'start_time':aMinT, 'duration':aDuration})

def convertListEpochToDateime(timelist):
    result = []
    for t in timelist:
        result.append(datetime.utcfromtimestamp(float(t)))
    return result

def plotGeneralIndividualData(activity, bat, reset, sync, firmware, app_version, inputType, input, sDate, eDate):
    
    print "Preparing data for plotting..."
    t = datetime.now()
    # activity
    atime = convertListEpochToDateime(activity['time'])
    steps = activity['steps']
    points = activity['points']

    # battery
    btime = convertListEpochToDateime(bat['time_corrected'])
    blevel = bat['rep_bat_lev']
    bfirmware = bat['firmware']
    
    # reset info
    rtime = convertListEpochToDateime(reset['time_corrected'])
    rcause = reset['reset_cause']
    r = 100
    if len(blevel) != 0:
        r = max(blevel)
    rs = [r] * len(rtime)
    prstime = []
    for i in xrange(0, len(rtime)):
        if rcause[i] == 'Power-on reset':
            prstime.append(rtime[i])
    prs = [r] * len(prstime)
    
    # sync info
    stime = convertListEpochToDateime(sync['epochTime'])
    fsync = sync['nFSync']
    ssync = sync['nSSync']

    # firmware
    ftime = convertListEpochToDateime(firmware['start_time'])
    fduration = firmware['duration']
    fw = firmware['firmware']
    for i in range(len(fw)):
        if fw[i] is None:
            continue
        afw = fw[i].split('.')
        afw = afw[len(afw) - 1]
        # print '{},{}'.format(i,afw)
        fw[i] = afw

    # app_version
    apptime = convertListEpochToDateime(app_version['start_time'])
    appduration = app_version['duration']
    app = app_version['app']
    

    fig = plt.figure(figsize=(15, 9))
    fig.suptitle('{}, from {} to {}'.format(input, sDate, eDate))

    colors = ['b', '0.8', 'g', 'r', '0.6', 'c', '0.4', 'm', '0.2', 'y', '0.1', 'k', 'w']
    colors = ['1.0', '0.9', '0.8', '0.7', '0.6', '0.5', '0.4', '0.3', '0.95', '0.85', '0.75', '0.65', '0.55', '0.45', '0.35', '0.25']

    t = datetime.now() - t
    print 'Done! Time taken: {}'.format(t)

    # prepare for firmware plot (old)
    # fwt = []
    # fw = []
    # afwt = []
    # pre_fw = None
    # for i in xrange(0, len(btime)):
    #     if bfirmware[i] != pre_fw:
    #         pre_fw = bfirmware[i]
    #         afwt = [btime[i]]
    #         fw.append(bfirmware[i])
    #         fwt.append(afwt)
    #     else:
    #         afwt.append(btime[i])

    # ax1 = fig.add_subplot(4,1,1)
    # h = 0
    # for i in xrange(0, len(fw)):
    #     afwt = fwt[i]
    #     afw = fw[i]
    #     h = h + 50
    #     y = [50] * len(afwt)
    #     print i
    #     ax1.bar(afwt, y, color = colors[i], edgecolor = colors[i], width = 0.005, label = afw, bottom = h-50)
    #     if i < len(fw) - 1:
    #         ax1.hold
        
    # plt.xlim(atime[0], atime[len(atime)-1])
    # ax1.set_xlabel('Time') # start_plot_t.isoformat(' '))
    # ax1.set_ylabel('Firmware')
    # plt.grid(True)    
    # ax1.legend(bbox_to_anchor=(-0.13, 1.4), loc=2, borderaxespad=0.)
    # #ax1.legend(loc = 2)
    
    h = 10
    fw_y = [h]*len(ftime)
    app_y = [h]*len(apptime)
    ax1 = fig.add_subplot(4,1,1)
    ax1.bar(ftime, fw_y, color = colors, width = fduration)
    for a,b,c in zip(ftime,fw_y,fw):
        ax1.text(a, b/2, '%.10s' % c, va= 'bottom')
    ax1.hold
    ax1.bar(apptime, app_y, color = colors, width = appduration, bottom = h)
    for a,b,c in zip(apptime,app_y,app):
        ax1.text(a, h+b/2, '%.10s' % c, va= 'bottom')
    plt.xlim(atime[0], atime[len(atime)-1])
    ax1.set_xlabel('Time') # start_plot_t.isoformat(' '))
    ax1.set_ylabel('Firmware - AppVersion')
    plt.grid(True)    

    ax1 = fig.add_subplot(4,1,2)
    ax1.bar(stime, ssync,  color = 'b' , label = 'successful_sync', bottom = fsync)
    if max(fsync) > 0:
        ax1.hold
        ax1.bar(stime, fsync,  color = 'r', label = 'failed_sync')
    plt.xlim(atime[0], atime[len(atime)-1])
    ax1.set_xlabel('Time') # start_plot_t.isoformat(' '))
    ax1.set_ylabel('# Syncs')
    plt.grid(True)    
    #ax1.legend(bbox_to_anchor=(0.005, 1), loc=2, borderaxespad=0.)
    ax1.legend(loc = 2)

    ax1 = fig.add_subplot(4,1,3)
    ax1.plot(btime, blevel, 'bo-', label = 'battery_level')
    if len(rtime) > 0:
        ax1.hold
        ax1.bar(rtime, rs, width = 0.005, color = 'gray', edgecolor = 'gray', label = 'reset')
    if len(prstime) > 0:
        ax1.hold
        ax1.bar(prstime, prs,  width = 0.005, color = 'r', edgecolor = 'r', label = 'power-on_reset')
    plt.xlim(atime[0], atime[len(atime)-1])
    ax1.set_xlabel('Time') # start_plot_t.isoformat(' '))
    ax1.set_ylabel('Battery Level (with Reset bars)')
    plt.grid(True)
    #ax1.legend(bbox_to_anchor=(0.005, 1), loc=2, borderaxespad=0., mode = "expand")
    ax1.legend(loc = 2)

    ax1 = fig.add_subplot(4,1,4)
    ax1.bar(atime, steps, color = 'c')
    plt.xlim(atime[0], atime[len(atime)-1])
    ax1.set_xlabel('Time') # start_plot_t.isoformat(' '))
    ax1.set_ylabel('Steps')
    plt.grid(True)

    #plt.ylim(0,22000)
    #plt.xlim(0,200)
    plt.grid(True)
    #plt.xticks(ticks)

    plt.show()
    fig.savefig('all_{}_{}_{}.png'.format(input, sDate, eDate ),dpi=400)


def passed(event):
    global plot_passed
    #global button_hit
    global bnext
    global bprev
    plot_passed = True
    print "PASSED"
    bprev.color = 'gray'
    bnext.color = 'green'
    #button_hit = False
    #plt.close('all')
   

def failed(event):
    global plot_passed
    #global button_hit
    global bnext
    global bprev
    print "FAILED"

    plot_passed = False
    bnext.color = 'gray'
    bprev.color = 'red'
    #button_hit = True
    #plt.close('all')


def plotActivityBatterryReset(bat, reset, input, sDate, eDate, params):
    global plot_passed
    global button_hit
    global bnext
    global bprev

    img_file_path = params['img_file_path']
    isRunningOnPi = params['isRunningOnPi'] 

    plot_passed = False
    btime = convertListEpochToDateime(bat['time_corrected'])
    blevel = bat['rep_bat_lev']
    bfirmware = bat['firmware']
    
    rtime = convertListEpochToDateime(reset['time_corrected'])
    rcause = reset['reset_cause']
   
    r = 100
    if len(blevel) != 0:
        r = max(blevel)
    rs = [r] * len(rtime)
    prstime = []
    for i in xrange(0, len(rtime)):
        if rcause[i] == 'Power-on reset':
            prstime.append(rtime[i])

    prs = [r] * len(prstime)

    
    fwt = []
    fw = []
    afwt = []
    pre_fw = None
    for i in xrange(0, len(btime)):
        if bfirmware[i] != pre_fw:
            pre_fw = bfirmware[i]
            afwt = [btime[i]]
            fw.append(bfirmware[i])
            fwt.append(afwt)
        else:
            afwt.append(btime[i])



    fig = plt.figure(figsize=(15, 9))
    fig.suptitle('{}, from {} to {}'.format(input, sDate, eDate))

    ax1 = fig.add_subplot(2,1,1)
    h = 0
    colors = ['b', '0.8', 'g', 'r', '0.6', 'c', '0.4', 'm', '0.2', 'y', '0.1', 'k', 'w', '0.9', '0.3']
    for i in xrange(0, len(fw)):
        afwt = fwt[i]
        afw = fw[i]
        h = h + 50
        y = [50] * len(afwt)
        print i
        ax1.bar(afwt, y, color = colors[i], edgecolor = colors[i], width = 0.005, label = afw, bottom = h-50)
        if i < len(fw) - 1:
            ax1.hold
        
    #plt.xlim(btime[0], btime[len(btime)-1])
    ax1.set_xlabel('Time') # start_plot_t.isoformat(' '))
    ax1.set_ylabel('Firmware')
    plt.grid(True)    
    ax1.legend(bbox_to_anchor=(-0.13, 1.1), loc=2, borderaxespad=0.)
    #ax1.legend(loc = 2)
    

    ax1 = fig.add_subplot(2,1,2)
    ax1.plot(btime, blevel, 'bo-', label = 'battery_level')
    if len(rtime) > 0:
        ax1.hold
        ax1.bar(rtime, rs, width = 0.005, color = 'gray', edgecolor = 'gray', label = 'reset')
    if len(prstime) > 0:
        ax1.hold
        ax1.bar(prstime, prs,  width = 0.005, color = 'r', edgecolor = 'r', label = 'power-on_reset')
    #plt.xlim(btime[0], btime[len(btime)-1])
    ax1.set_xlabel('Time') # start_plot_t.isoformat(' '))
    ax1.set_ylabel('Battery Level (with Reset bars)')
    plt.grid(True)
    #ax1.legend(bbox_to_anchor=(0.005, 1), loc=2, borderaxespad=0., mode = "expand")
    ax1.legend(loc = 2)

    #MICHAELS CODE -- run this if not running on a Raspberry Pi
    if not isRunningOnPi:
        axprev = plt.axes([0.7, 0.05, 0.1, 0.075])
        axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
        bnext = Button(axnext, 'Pass')
        bprev = Button(axprev, 'Fail')
        
        bnext.color = 'gray'
        bprev.color = 'gray'
        bnext.on_clicked(passed)
        bprev.on_clicked(failed)
    #END MICHAELS CODE
    
    plt.show(block=True)

    # **** testing for Raspberry Pi ****
    if isRunningOnPi:
        target_file = img_file_path
        print "Saving file %s" % target_file
        plt.savefig(target_file)
        plot_passed = startGui()
    return plot_passed


def getHistSyncData(database, sDate, eDate, syncDate):
    print '{}, {}, {}'.format(database, sDate, eDate)
    
    cursor = connectToDB(database)
    print '\nGetting data from database...'
    
    if eDate == None:
        eDate = sDate

    s = '{}'.format(sDate)
    if eDate != sDate:
        s = '{} - {}'.format(sDate, eDate)

    sync_file = open('hist_sync_{}.csv'.format(s), 'w')

    format = "%Y-%m-%d"
    # datetime
    startD = datetime.strptime(sDate, format)
    endD = datetime.strptime(eDate, format)
    # epoch time
    startD = calendar.timegm(startD.timetuple())
    endD = calendar.timegm(endD.timetuple())

    num_days = 1 + (int) ((endD - startD)/(24*60*60))

    t = datetime.now()

    # --- get sync ---
    query = '''
select email,
    count(case when basename = 'debug_log.txt' then 1 else null end) num_sync,
    count(case when basename = '0101' then 1 else null end) num_successful_sync
from sync_log_file
where date >= '{}' and date <= '{}' 
group by email
having email in (
    select distinct email
    from user_raw_data
    where date_trunc('day', sync_end) = '{}' 
    and email in (
        select email
        from user_raw_data
        group by email
        having min(sync_end) < ('{}'::date - INTERVAL '3 week')
        )
    )
;
'''.format(sDate, eDate, syncDate, syncDate);

    # print query
    cursor.execute(query);
    t = datetime.now() - t
    print 'Done! Querying time: {}'.format(t)

    t = datetime.now()

    sync_email = []
    sync = []
    sync_success = []

    s = 'email, num_sync, num_succ_sync'
    sync_file.write("%s\n" % s)
    i = 0
    row = cursor.fetchone()
    while row:
        sync_email.append(row[0])

        n1 = (int) (row[1]/num_days)
        if n1 <= 30:
            sync.append(n1)
        else:
            sync.append(31)
        
        n2 = (int) (row[2]/num_days)
        if n2 <= 20:
            sync_success.append(n2)
        else:
            sync_success.append(21)

        s = '{},{},{}'.format(row[0],n1,n2)
        sync_file.write("%s\n" % s)
        
        row = cursor.fetchone()
    
    t = datetime.now() - t
    print 'Done! Processing time for sync: {}'.format(t)
 
    closeDB(cursor)
    return (sync_email, sync, sync_success)

    
def getHistActivityData(database, sDate, eDate, syncDate):
    #print '{}, {}, {}'.format(database, sDate, eDate)
    
    cursor = connectToDB(database)
    print '\nGetting data from database...'
    
    if eDate == None:
        eDate = sDate

    format = "%Y-%m-%d"
    # datetime
    startD = datetime.strptime(sDate, format)
    endD = datetime.strptime(eDate, format)
    # epoch time
    startD = calendar.timegm(startD.timetuple())
    endD = calendar.timegm(endD.timetuple())

    num_days = 1 + (int) ((endD - startD)/(24*60*60))

    s = '{}'.format(sDate)
    if eDate != sDate:
        s = '{} - {}'.format(sDate, eDate)

    dtap_file = open('hist_dtap_{}.csv'.format(s), 'w')
    ttap_file = open('hist_ttap_{}.csv'.format(s), 'w')
    point_file = open('hist_points_{}.csv'.format(s), 'w')

    t = datetime.now()

    query = '''
select email, double_tap_sum_local, triple_tap_sum_local, point_sum_local
from user_daily_data
where record_date >= '{}' and record_date <= '{}'
and email in (
    select distinct email
    from user_raw_data
    where date_trunc('day', sync_end) = '{}' 
    and email in (
        select email
        from user_raw_data
        group by email
        having min(sync_end) < ('{}'::date - INTERVAL '3 week')
        )
    )
;
'''.format(sDate, eDate, syncDate, syncDate);

    # print query
    cursor.execute(query);
    print 'Done!'
    t = datetime.now() - t
    print 'Querying time: {}'.format(t)
    t = datetime.now()

    a_email = []
    dtaps = []
    ttaps = []
    points = []
  
    dtap_file.write("email, num_dtaps\n")
    ttap_file.write("email, num_ttaps\n")
    point_file.write("email, points\n")
    
    row = cursor.fetchone()
    while row:
        a_email.append(row[0])
        
        n = (int) (row[1])
        if n <= 100:
            dtaps.append(n)
        else: 
            dtaps.append(101)

        s = '{},{}'.format(row[0],n)
        dtap_file.write("%s\n" % s)
        
        
        n = (int) (row[2])
        if n <= 50:
            ttaps.append(n)
        else:
            ttaps.append(51)

        s = '{},{}'.format(row[0],n)
        ttap_file.write("%s\n" % s)
        
        n = (int) ((float) (row[3])/2.5)
        if n <= 3000:
            points.append(n)
        else:
            points.append(3001) 

        s = '{},{}'.format(row[0],n)
        point_file.write("%s\n" % s)

        row = cursor.fetchone()

    t = datetime.now() - t
    print 'Done! Processing time for activity: {}'.format(t)

    closeDB(cursor)
    return (a_email, dtaps, ttaps, points)


def plotHistData(sync_email, sync, sync_success, a_email, dtaps, ttaps, points, sDate, eDate):

    if eDate == None:
        eDate = sDate
    
    s = '{}'.format(sDate)
    if eDate != sDate:
        s = '{} - {}'.format(sDate, eDate)

    plotHistogram(sync_success, max(sync_success) + 1,'syncs', s)
    plotHistogram(dtaps, max(dtaps) + 1, 'dtaps', s)
    plotHistogram(ttaps, max(ttaps) + 1, 'ttaps', s)
    plotHistogram(points, 100, 'points', s)

def plotHistogram(data, num_bin, data_name, period ):

    fig = plt.figure(figsize=(8, 6))
    fig.suptitle('\nHistogram of {}, {}, #users: {}'.format(data_name, period, len(data)))
    ax1 = fig.add_subplot(111)
    print '{}, #bins: {}, max: {}'.format(data_name, num_bin, max(data))
    ax1.hist(data, num_bin)
    ax1.set_xlabel('{}'.format(data_name)) # start_plot_t.isoformat(' '))
    ax1.set_ylabel('count')
    plt.grid(True)
    fig.savefig('hist_{}_{}.png'.format(data_name, period),dpi=400)


def getHistMinuteSmallVariance(database, sDate, eDate, syncDate):
    print '{}, {}, {}'.format(database, sDate, eDate)
    
    cursor = connectToDB(database)
    print '\nGetting data from database...'
    
    if eDate == None:
        eDate = sDate

    format = "%Y-%m-%d"
    # datetime
    startD = datetime.strptime(sDate, format)
    endD = datetime.strptime(eDate, format)
    # epoch time
    startD = calendar.timegm(startD.timetuple())
    endD = calendar.timegm(endD.timetuple())

    num_days = 1 + (int) ((endD - startD)/(24*60*60))

    t = datetime.now()

    # --- get sync ---
    query = '''
select email, variance_local   
from user_daily_data
where record_date >= '{}' and record_date <= '{}' 
and email in (
    select distinct email
    from user_raw_data
    where date_trunc('day', sync_end) = '{}' 
    and email in (
        select email
        from user_raw_data
        group by email
        having min(sync_end) < ('{}'::date - INTERVAL '3 week')
        )
    )
;
'''.format(sDate, eDate, syncDate, syncDate);

    # print query
    cursor.execute(query);
    t = datetime.now() - t
    print 'Done! Querying time: {}'.format(t)

    t = datetime.now()

    e = []
    v = []

    i = 0
    row = cursor.fetchone()
    while row:
        e.append(row[0])

        c = 0
        for r in row[1]:
            if r < 50:
                c = c + 1

        v.append(c)

        # print row[1]
        row = cursor.fetchone()
    #print v
    closeDB(cursor)

    s = '{}'.format(sDate)
    if eDate != sDate:
        s = '{} - {}'.format(sDate, eDate)
    
    fig = plt.figure(figsize=(8, 6))
    fig.suptitle('\nHistogram of # Minutes with Small Variance (<50), {}, #users: {}'.format(s, len(v)))
    ax1 = fig.add_subplot(111)
    #print max(dtaps)
    ax1.hist(v, 102)
    ax1.set_xlabel('# Minutes') # start_plot_t.isoformat(' '))
    ax1.set_ylabel('Count')
    plt.grid(True)
    fig.savefig('hist_minutes_variance_{}.png'.format(s),dpi=400)

def getHistDailySmallPoints(database, sDate, eDate, syncDate):
    print '{}, {}, {}'.format(database, sDate, eDate)
    
    cursor = connectToDB(database)
    print '\nGetting data from database...'
    
    if eDate == None:
        eDate = sDate

    format = "%Y-%m-%d"
    # datetime
    startD = datetime.strptime(sDate, format)
    endD = datetime.strptime(eDate, format)
    # epoch time
    startD = calendar.timegm(startD.timetuple())
    endD = calendar.timegm(endD.timetuple())

    num_days = 1 + (int) ((endD - startD)/(24*60*60))

    t = datetime.now()

    # --- get sync ---
    query = '''
select email,
count(case when point_sum_local < 125 then 1 else null end) days_point_less_125
--select count(1)
from user_daily_data
where record_date >= '{}' and record_date <= '{}'
group by email
having email in (
    select distinct email
    from user_raw_data
    where date_trunc('day', sync_end) = '{}' 
    and email in (
        select email
        from user_raw_data
        group by email
        having min(sync_end) < ('{}'::date - INTERVAL '3 week')
        )
    )
;
'''.format(sDate, eDate, syncDate, syncDate);

    # print query
    cursor.execute(query);
    t = datetime.now() - t
    print 'Done! Querying time: {}'.format(t)

    t = datetime.now()

    emails = []
    days = []

    i = 0
    row = cursor.fetchone()
    while row:
        emails.append(row[0])
        days.append(row[1])
        # print row[1]
        row = cursor.fetchone()
    #print v
    closeDB(cursor)

    s = '{}'.format(sDate)
    if eDate != sDate:
        s = '{} - {}'.format(sDate, eDate)
    
    fig = plt.figure(figsize=(8, 6))
    fig.suptitle('\nHistogram of # Days having Points < 50, {}, #users: {}'.format(s, len(days)))
    ax1 = fig.add_subplot(111)
    #print max(dtaps)
    ax1.hist(days, num_days)
    ax1.set_xlabel('#Days') # start_plot_t.isoformat(' '))
    ax1.set_ylabel('Count')
    plt.grid(True)
    fig.savefig('hist_days_small_points_{}.png'.format(s),dpi=400)

def getHWLogEntries(database, inputType, input, sDate, eDate):

    if inputType != 'email' and inputType != 'serial_number':
        print 'Input type must be email or serial_number'
        return []

    cursor = connectToDB(database)
    print '\nGetting hardware logs from database...'
    
    t = datetime.now()

    query = '''
select urd.sync_end sync_time, event_index entry_index, hw.event_timestamp entry_timestamp, tz_offset/60 timezone, firmware, primary_code, secondary_code, hw.data 
from hardware_log hw inner join user_raw_data urd on (hw.user_raw_data_id = urd.user_raw_data_id)
where {} = '{}'
and sync_end >= '{}'
and sync_end <= '{}'
order by sync_end, hw.event_index
;
'''.format(inputType, input, sDate, eDate);
    
    # print query
    cursor.execute(query);
    print 'Done!'
    t = datetime.now() - t
    print 'Querying time: {}'.format(t)
    t = datetime.now()

    data = []
    row = cursor.fetchone()
    while row:
        sync_time = convertToUserLocalTime(row[0], row[3])
        entry_time = convertToUserLocalTime(row[2], row[3])
        r = {'sync_time': sync_time, 'entry_index':row[1], 'entry_timestamp':entry_time, 'timezone':row[3], 'firmware':row[4], 'primary_code':row[5], 'secondary_code':row[6], 'content':row[7]}
        data.append(r)
        
        row = cursor.fetchone()

    #print str_data
    closeDB(cursor)

    return data

def getSyncMetaData(database, inputType, input, sDate, eDate):
    if inputType != 'email' and inputType != 'serial_number':
        print 'Input type must be email or serial_number'
        return []

    cursor = connectToDB(database)
    print '\nGetting data from database...'
    
    t = datetime.now()

    format = "%Y-%m-%d"
    # datetime
    startD = datetime.strptime(sDate, format)
    endD = datetime.strptime(eDate, format)
    # epoch time
    startD = calendar.timegm(startD.timetuple())
    endD = calendar.timegm(endD.timetuple())

    query = '''
select sync_start d,
    count(case when basename = '0101' then 1 else null end) is_successful
from sync_log_file
where {} = '{}'
    and date >= '{}' 
    and date <= '{}'
group by sync_start
order by sync_start;
'''.format(inputType, input, sDate, eDate);

    
    # print query
    cursor.execute(query);
    print 'Done!'
    t = datetime.now() - t
    print 'Querying time: {}'.format(t)

    data = []

    row = cursor.fetchone()
    while row:
        t = datetime.utcfromtimestamp(float(row[0]))
        r = {'epochTime':row[0], 'time': t, 'is_successful': row[1]}
        #print 'Sync Time: {}, Successful: {}'.format(t, row[1])
        data.append(r)
        
        row = cursor.fetchone()


    #print time
    #print steps
    closeDB(cursor)

    return data

def usage():
    print USAGE_TEXT
    sys.exit(-1)

def test1(argv):
    print 

def main(argv):

    ###################
    if len(argv) < 5:
        usage()

    database = argv[0]
    #inputType = 'serial_number'
    inputType = argv[1]
    input = argv[2]
    startDate = argv[3]
    endDate = argv[4]

    #cur = connectToDB(database)
    #------------
    #result = getSyncBatteryDataByEmail(cur, email, startDate, endDate)
    #plotSyncBattery(result)

    #------------
    #result = getEntryBatteryDataByEmail(database, email, startDate, endDate)
    #print result
    #entry_data = prepareBatteryInfoToPlot(result)
    #plotEntryBattery(entry_data, email)

    #-------------
    (bat,reset) = getBatteryWithResetData(database, inputType, input, startDate, endDate)
    activity = getDailyActivity(database, inputType, input, startDate, endDate)
    (syncs, sync) = getNumSync(database, inputType, input, startDate, endDate)
    (firmware, app_version) = getFirmwareAppVersion(database, inputType, input, startDate, endDate)
    data = getSyncMetaData(database, inputType, input, startDate, endDate)
    
    plotGeneralIndividualData(activity, bat, reset, sync, firmware, app_version, inputType, input, startDate, endDate)
    
    #-------------
    # database = 'shine_test'
    # emails = ['thinh@misfitwearables.com', 'thy@misfitwearables.com', 'tung@misfitwearables.com']
    # #emails = ['thinh@misfitwearables.com']    
    # for email in emails:
    #     (bat,reset) = getBatteryWithResetData(database, 'email', input, startDate, endDate)
    #     activity = getDailyActivity(database, 'email', input, startDate, endDate)
    #     sync = getNumSync(database, 'email', input, startDate, endDate)

    #     plotGeneralIndividualData(activity, bat, reset, sync, firmware, inputType, input, startDate, endDate)

    #-----------
    # (a, b) = getHWLogEntries(database, inputType, input, startDate, endDate)
    # print '\n\n\n\n'
    # print b

    #-------------
    #(bat,reset) = getBatteryWithResetData(database, 'serial_number', input, startDate, endDate)
    #plotBatterryResetBySerialNumber(bat, reset, input, startDate, endDate)

    ##################
    #cur = connectToDB('shine_prod')
    #fw = '0.0.50r'
    #(x,y) = getHistogramUsersByFirmware(cur, fw)
    #plotHistogramUsersByFirmware(fw, x, y, True)


    ##################
    #cur = connectToDB('shine_prod')
    #(x,y1,y2,y3,y4, y5) = getNumUserByDateFirmware(cur)
    #plotNumUserByDateFirmware(x,y1,y2,y3,y4,y5)
    #plt.show()

    ####################
    #syncDate = '2013-11-20'
    #sDate = '2013-11-13'
    #eDate = None
    #eDate = '2013-11-19'
    #(sync_email, sync, sync_success) = getHistSyncData('shine_prod', sDate, eDate, syncDate)
    #(a_email, dtaps, ttaps, points) = getHistActivityData('shine_prod', sDate, eDate, syncDate)
    #plotHistData(sync_email, sync, sync_success, a_email, dtaps, ttaps, points, sDate, eDate)

    #for sDate in ['2013-11-13', '2013-11-14', '2013-11-15', '2013-11-16', '2013-11-17', '2013-11-18', '2013-11-19']:
        #(sync_email, sync, sync_success) = getHistSyncData('shine_prod', sDate, eDate, syncDate)
        #(a_email, dtaps, ttaps, points) = getHistActivityData('shine_prod', sDate, eDate, syncDate)
        #plotHistData(sync_email, sync, sync_success, a_email, dtaps, ttaps, points, sDate, eDate)
    
    #-------------
    #getHistMinuteSmallVariance('shine_prod', sDate, eDate, syncDate)
    
    #---------
    #getHistDailySmallPoints('shine_prod', sDate, eDate, syncDate)    


    #closeDB(cur)


    
if __name__ == "__main__":
    main(sys.argv[1:])




