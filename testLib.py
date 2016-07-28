# import automation libraries
from AutoLib import *

import sys
from shutil import copyfile
import os

# debug and display flags
debuging = True
display = False

testLogFile = 'test/test-autoLog.txt'
refrenceLogFile = 'test/test-autoLog-ref.txt'

### Testing Functions ###

# create a schedule object from an xml schedule
def createSchedule(scheduleFile):
  scheduleObject = schedule(scheduleFile)
  scheduleObject.setTestMode(1)
  return scheduleObject

# set test mode for schedule
def setTestMode(mode):
  scheduleObject.setTestMode(mode)

# update the schedule object with an xml file
def updateSchedule(scheduleObject, scheduleFile):
  scheduleObject.update(scheduleFile)

# simulate running a schedule for all times for all days
def testWeek(schedule):
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for day in days:
        testTimes(schedule, day)

# simulate running a schedule for all dates for a given time and year
# year as 2 digit abreviation
def testYear(schedule, year, hour = None, minute = None, second = None):
    for month in range(1, 13):
        for day in range(1, 32): # may test non existant days on months with less than 31 days
            date = "{}/{}/{}".format(month, day, year)
            testCase(schedule, None, hour, minute, second, date)
            if schedule.getTestMode() > 2:
              sys.stdout.write('*')

# simulate running a schedule for all days for a given time
def testDays(schedule, hour = None, minute = None, second = None):
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for day in days:
        testCase(schedule, day, hour, minute, second)

# simulate running a schedule for all times for a given day or date
def testTimes(schedule, day = None, date = None):
    second = 0 # seconds not currently used
    for hour in range(0, 24):
        if schedule.getTestMode() > 2:
          sys.stdout.write('*')
        for minute in range(0, 60):
                testCase(schedule, day, hour, minute, second, date)

# test a schedule against a defined set of datetime parameters
def testCase(schedule, day = None, hour = None, minute = None, second = None, date = None):
    # set the time object
    schedule.now.set(day, hour, minute, second, date)
    if display:  print day, hour, minute, second, date
    # check for events and run any current ones
    if schedule.checkEvents():
        schedule.playCurrentEvent()

# check schedule actions log against a refrence log
def logCompare(testFile):
    index = 0
    # open file streams
    with open(testFile) as testLog:
        with open(refrenceLogFile) as refLog:  
            # read in first lines      
            refLine = refLog.readline()
            testLine = testLog.readline()
            # compare lines untill a log stream has ended
            while refLine != "" and testLine != "":
                index += 1
                # check if log line are same
                if refLine != testLine:
                    print "Test Log not consistent with Refrence Log: Mismatch on line", index
                    print "Reference Log - ", refLine
                    print "Test Log - ", testLine

                # read next lines from logs
                refLine = refLog.readline()
                testLine = testLog.readline()

            # if both streams ended simultaniusly then report same length
            if refLine == "" and testLine == "":
                print "Logs are the same length"
            # else report which stream ended earlier
            elif refLine == "":
                print "Reference Log ended before Test Log"
            elif testLine == "":
                print "Test Log ended before Reference Log"


# make current log the refrence log
def setRefrenceLog():
    # remove old refrenceLogFile
    try:
        os.remove(refrenceLogFile)
    except: pass
    # copy logFile to new refrenceLogFile
    try:
        copyfile(testLogFile, refrenceLogFile)
    except:
        print 'Failed to Set Refrence Log!'
