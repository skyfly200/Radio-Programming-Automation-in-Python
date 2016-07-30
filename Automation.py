# import automation libraries
from AutoLib import *

# import tendo singleton class
import singleton

# create singleton lock
instance = singleton.SingleInstance()

# debug flags
debuging = True
prtSchedule = False

# how long to wait between loops in minutes
wait = 1
# variable stores the time the loop was last run
# initialized to the time - the wait time, so the first run of the loop happens imediately
lastLoop = (int(time.strftime("%H")) * 60) + int(time.strftime("%M")) - wait

# path of the schedule xml file
scheduleFile = 'schedule.xml'

# create a schedule object
automationSchedule = schedule(scheduleFile)
# interval of schedule updates
updateTime = 60 # update every hour

print "Automation Started - ", automationSchedule.now.getDatetimeStr()
automationSchedule.actionLog.logRaw("Automation Started", automationSchedule.now)

try:
	# infinite loop
	while True:
		# sync the time object
		automationSchedule.now.sync()
		# if schedule update interval has passed
		if (int(time.strftime("%H")) * 60) + int(time.strftime("%M")) % updateTime == 0:
			automationSchedule.update(scheduleFile)
		# if wait interval has passed, run the next check
		if automationSchedule.now.getInMinutes() >= (lastLoop + wait) % 1440 :
			# update last loop string
			lastLoop = automationSchedule.now.getInMinutes()
			# check schedule for current events
			if automationSchedule.checkEvents():
				# play any curently events
				automationSchedule.playCurrentEvent()
				# print the schedule if flag is enabled
				if prtSchedule: automationSchedule.printRawEvents()
				
		else:
			time.sleep(5)

except KeyboardInterrupt:
	print "Automation Exited - ", automationSchedule.now.getDatetimeStr()
	automationSchedule.actionLog.logRaw("Automation Exited", automationSchedule.now)
	# delete instance lock
	del instance
	
except:
	print "Automation Exited - ", automationSchedule.now.getDatetimeStr()
	automationSchedule.actionLog.logRaw("Automation Exited", automationSchedule.now)