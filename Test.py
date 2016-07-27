# import automation libraries
import testLib


# path of the test schedule xml file
testScheduleFile = 'test/test-schedule.xml'

testSchedule = testLib.createSchedule(testScheduleFile)
testSchedule.setTestMode(3)

## Run Tests ##

print "Begining Test"
testLib.testWeek(testSchedule)
testScheduleFile = 'test/test-schedule1.xml'
testLib.updateSchedule(testSchedule, testScheduleFile)
testLib.testYear(testSchedule, 16, 23)
print "Test Competed"



