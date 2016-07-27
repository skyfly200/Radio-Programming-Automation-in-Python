# import automation libraries
from AutoLib import *

import sys

# debug and display flags
debuging = True
display = False

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

