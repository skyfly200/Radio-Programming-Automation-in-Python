# import automation libraries
import testLib
import os

# remove test log from previous run
try:
  os.remove(testLib.testLogFile)
except: pass

# path of the test schedule xml file
testScheduleFile = "test/test-schedule.xml"

testSchedule = testLib.createSchedule(testScheduleFile)
testSchedule.setTestMode(3)

# uncomment this to set the refrence log
# currently not working
#testLib.setRefrenceLog()

## Run Tests ##

print "Begining Test"
testLib.testWeek(testSchedule)
testScheduleFile = "test/test-schedule1.xml"
testLib.updateSchedule(testSchedule, testScheduleFile)
testLib.testYear(testSchedule, 16, 23)
print "Test Competed"

testLib.logCompare(testLib.testLogFile)



