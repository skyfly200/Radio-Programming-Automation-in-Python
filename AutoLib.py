import clever as winampCtrl
import xml.etree.ElementTree as xmlProcessor
import os.path, re, random, time#, win32api
from ctypes import Structure, windll, c_uint, sizeof, byref

# class for manipulating the log file
class log(object):
	# open or create log file
	def __init__(self, path="log.txt", name="Winamp Automation"):
		self.logPath = path
		self.logName = name
		# check if file exists
		exists = os.path.isfile(self.logPath)
		# if log file dosn't exist, then create it and write the header line
		if not exists:
			with open(self.logPath, 'a') as f:
				f.write("---" + self.logName + " Log File---\n")
		
	# return a log string representing a specified action and its arg
	def makeLog(self, action, arg=""):
		# get the action type from its tag
		actionType = action.tag # get the actions type
		# return log string for default action
		if actionType == "default": 
			return actionType + " - " + arg + "\n"
		# build action log for a playlist, show or drop
		else:
			actionName = str(action.get('name'))
			actionTime = ""
			# set the actionTime for shows or playlists
			if actionType == "show" or actionType == "playlist": 
				start = action.find('time').get('start')
				end = action.find('time').get('end')
				actionTime = " < " + start + " - " + end + " > "
			# set the actionTime for drops
			elif actionType == "drop":
				frequency = action.find('freq').text
				actionTime = " < Every " + frequency + " Min > "
			# build and return the log string
			return actionType + " - " + actionName + actionTime + arg + "\n"
			
	# log an action in the log file
	def logAction(self, action, time, arg=''):
		# create a log string
		log = self.makeLog(action, arg)
		# write the action to the log 
		with open(self.logPath, 'a') as f:
			f.write(time.getDatetimeStr() + " :\n" + log)
		
	# log any value to the log file
	def logRaw(self, log, time):
		with open(self.logPath, 'a') as f:
			f.write(time.getDatetimeStr() + " :\n" + str(log) + "\n")
	
	# return the last log in the log file
	def lastLog(self):
		log = False
		with open(self.logPath) as f:
			try:
				log = f.readlines()[-1] + f.readlines()[-1][5:]
			except:
				log = ""
		return log
	
	# return the timestamp of the last log in the log file
	def lastLogTime(self):
		timestamp = False
		with open(self.logPath) as f:
			timestamp = f.readlines()[-2][:-3]
		return timestamp

	# return the action of the last log in the log file
	def lastLogAction(self):
		action = False
		with open(self.logPath) as f:
			action = f.readlines()[-1]
		return action

	# compare an action against last logged action
	def matchLog(self, compare):
		return compare == self.lastLogAction()

# struct for idle time calculation
class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]
	
# returns seconds system has been idle
def get_idle_duration():
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = sizeof(lastInputInfo)
    windll.user32.GetLastInputInfo(byref(lastInputInfo))
    millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
    return millis / 1000.0
		
class datetime():
	# instantiate a datetime object
	def __init__(self):
		# set the object state to the current time
		self.timeHours = int(time.strftime("%H"))
		self.timeMinutes = int(time.strftime("%M"))
		self.timeSeconds = int(time.strftime("%S"))
		self.timeInMinutes = (self.timeHours * 60) + self.timeMinutes
		self.timeStr = time.strftime("%H:%M")
		self.dayStr = time.strftime("%a")
		self.dateStr = time.strftime("%m/%d/%y")
		self.datetimeStr = self.timeStr + " " + self.dayStr + " " + self.dateStr

	# sync datetime object to the current time
	def sync(self):
		# set the object state to the current time
		self.timeHours = int(time.strftime("%H"))
		self.timeMinutes = int(time.strftime("%M"))
		self.timeSeconds = int(time.strftime("%S"))
		self.timeInMinutes = (self.timeHours * 60) + self.timeMinutes
		self.timeStr = time.strftime("%H:%M")
		self.dayStr = time.strftime("%a")
		self.dateStr = time.strftime("%m/%d/%y")
		self.datetimeStr = self.timeStr + " " + self.dayStr + " " + self.dateStr
		
	# set time manualy for testing 
	def set(self, day = None, hour = None, minute = None, second = None, date = None):
		if hour == None: hour = 0
		self.timeHours = int(hour)
		if minute == None: minute = 0
		self.timeMinutes = int(minute)
		if second == None: second = 0
		self.timeSeconds = int(second)
		self.timeInMinutes = (self.timeHours * 60) + self.timeMinutes
		self.timeStr = '{}:{}'.format(str(self.timeHours).zfill(2), str(self.timeMinutes).zfill(2))
		if day == None: day = time.strftime("%a")
		self.dayStr = day
		if date == None: date = time.strftime("%m/%d/%y")
		self.dateStr = date
		self.datetimeStr = '{} {} {}'.format(self.timeStr, self.dayStr, self.dateStr)

	# get functions for datetime member variables
	def getHours(self): 
		return self.timeHours

	def getMinutes(self): 
		return self.timeMinutes
		
	def getInMinutes(self): 
		return self.timeInMinutes
		
	def getTimeStr(self): 
		return self.timeStr
		
	def getDayStr(self): 
		return self.dayStr
		
	def getDateStr(self): 
		return self.dateStr
		
	def getDatetimeStr(self): 
		return self.datetimeStr

	# check if a date code matches today
	def checkDay(self, dayCode):
		# define regular expresions for difrent date code formats
		listEx = re.compile(r'([0-9a-z/]{3,9}, ?)+[0-9a-z/]{3,9}', re.I)

		# if code matched todays weekday
		if re.match(self.dayStr, dayCode, re.I):
			return True
		
		# if todays date
		elif dayCode == self.getDateStr():
			return True
			
		# if a multi day code then check each item
		elif listEx.match(dayCode):
			for i in dayCode.split(','):
				if self.checkDay(i.strip()):
					return True
					
		# if code is ALL then always return true
		elif dayCode.upper() == "ALL":
			return True
			
		return False


class schedule():
	# instantiate a schedule object
	def __init__(self, xmlFile):
		# init testing flag to 0 (0 is OFF, 1 is ON, 2 holds control ops)
		self.testing = 0
		# parse the xml file
		self.update(xmlFile);
		# initialize lists for current events
		self.currentShow = None
		self.currentPlaylist = None
		self.currentDrops = []
		# create a datetime object for checking the current time
		self.now = datetime()
		# create new log objects to log actions and errors
		self.actionLog = log("logs/autoLog.txt", "Automation Actions")
		self.errorLog = log("logs/errorLog.txt", "Automation Errors")
		

	# update the schedule object with provided xml file
	def update(self, xmlFile):
		# parse the xml file
		root = self.parseXML(xmlFile)
		# Look for events in the schedule xml structure
		self.shows = root.findall('show')
		self.playlists = root.findall('playlist')
		self.drops = root.findall('drop')
		self.defaults = root.findall('default')

	# get test mode 
	def getTestMode(self):
		return self.testing

	# set test mode 
	def setTestMode(self, mode):
		self.testing = mode
		# create new log objects to log actions and errors
		if self.testing > 0: # test logging
			self.actionLog = log("test/test-autoLog.txt", "Automation Actions")
			self.errorLog = log("test/test-errorLog.txt", "Automation Errors")
		else: # normal logging
			self.actionLog = log("logs/autoLog.txt", "Automation Actions")
			self.errorLog = log("logs/errorLog.txt", "Automation Errors")

	# process the xml file object
	def parseXML(self, xmlFile):
		scheduleFile = xmlProcessor.parse(xmlFile)
		return scheduleFile.getroot()

	# check for current events
	def checkEvents(self):	
		# empty the lists for current events
		self.currentShow = None
		self.currentPlaylist = None
		self.currentDrops = []
		# new events flag
		newEvent = False
		# priority default value
		priority = 100	
		if self.testing == 0: # stop time sync when testing
			# sync the time object to the current time
			self.now.sync()
		# Check for current show	
		for show in self.shows:
			# process shows day, time and priority info
			day = show.find('day').get('code')
			startMinute = parseEventTime(show, 'start')
			endMinute = parseEventTime(show, 'end')
			showPriority = int(show.find('priority').text)
			# check show date and time agianst current date and time 
			minutesNow = self.now.getInMinutes() 
			if minutesNow >= startMinute and minutesNow < endMinute and self.now.checkDay(day):
				# check show priority
				if showPriority < priority:
					newEvent = True
					self.currentShow = show
			
			
		# Check for current playlist
		priority = 100
		for playlist in self.playlists:
			# process playlist day, time and prority info
			day = playlist.find('day').get('code')
			startMinute = parseEventTime(playlist, 'start')
			endMinute = parseEventTime(playlist, 'end')
			playlistPriority = int(playlist.find('priority').text)
			# check playlist date and time agianst current date and time  
			if self.now.getInMinutes() >= startMinute and self.now.getInMinutes() < endMinute and self.now.checkDay(day):
				# check playlist priority
				if playlistPriority < priority:
					priority = playlistPriority
					self.currentPlaylist = playlist
					newEvent = True
					
		
		# Check for current drops
		for drop in self.drops:
			# process drop playback info
			freq = drop.find('freq').text
			code = drop.find('day').get('code')
			# check drop date agianst current date
			if (self.now.getInMinutes() % int(freq)) == 0 and self.now.checkDay(code):
				self.currentDrops.append(drop)
				newEvent = True
		
		# return if there are any new events to run
		return newEvent
				
			
	def playCurrentEvent(self):
		
		# set default priority and event
		priority = 100
		
		idleWaitTime = 30 # seconds to wait for idle before running playlists or drops
		idleWait = False
		
		# if there is a scheduled show, check if show is not already playing, then play it
		if self.currentShow is not None:
			if !self.actionLog.matchLog(self.actionLog.makeLog(self.currentShow, "")):
				if self.testing < 3:	print "Show: ", self.currentShow.get('name'), "\nTime Slot:", self.currentShow.find('time').get('start'), "-", self.currentShow.find('time').get('end')
				# control winamp as long as not in test mode 2
				if self.testing < 2: 
					# if playing something then fade out
					if winampCtrl.status() == 1:
						winampCtrl.fadeOut()
					# play show, fade in and log the show
					winampCtrl.loadplay(self.currentShow.find('file').get('path'))
					winampCtrl.volmax()
				self.actionLog.logAction(self.currentShow, self.now)
			
		# else if the computer is idle, then look for other current events
		elif not idleWait or get_idle_duration() >= idleWaitTime:
			# check if there are any current drops to play
			if len(self.currentDrops) > 0:
				# wait for current song to end
				# skips if playing a stream
				if self.testing < 3:	print "\nplaying drop after song"
				self.waitforend()		

				# play all current drops
				for drop in self.currentDrops:
					# control winamp as long as not in test mode 2
					if self.testing < 2: 
						# make sure shuffle is on
						if winampCtrl.getshuffle() == 0: 
							winampCtrl.swshuffle()
						# load the drop
						winampCtrl.loadplay(drop.find('file').get('path'))
					# print drop info and log the event
					if self.testing < 3:	print "\nDrop: " + drop.get('name'), " Frequency: ", drop.find('freq').text, "Min"	
					self.actionLog.logAction(drop, self.now)				
					# wait for drop to end before continuing
					self.waitforend()
					
			# if there is a current playlist make sure its not already playing
			if self.currentPlaylist is not None:
				if !self.actionLog.matchLog(self.actionLog.makeLog(self.currentShow, "")):
					# control winamp as long as not in test mode 2
					if self.testing < 2:
						# make sure shuffle is on
						if winampCtrl.getshuffle() == 0: winampCtrl.swshuffle()
						winampCtrl.loadplay(self.currentPlaylist.find('file').get('path'))
					if self.testing < 3:	print "\nPlaylist: " + self.currentPlaylist.get('name'), "\nTime Slot:", self.currentPlaylist.find('time').get('start'), "-", self.currentPlaylist.find('time').get('end')
					self.actionLog.logAction(self.currentPlaylist, self.now)
		
	# when no playlist or show is scheduled and there are defaults, then randomly load one
	def gotoDefault(self):
			if (len(self.defaults) > 0): 
				# randomly choose a default from the list
				default = random.choice(self.defaults)
				path = str(default.find('file').get('path'))
				if self.actionLog.lastLog() != self.actionLog.makeLog(default, path):
					if self.testing < 3:	print "\nGoing to default - ", path
					self.actionLog.logAction(default, self.now, path)
					# control winamp as long as not in test mode 2
					if self.testing < 2:
						winampCtrl.loadplay(path)
			else:
				if self.testing < 3:	print "\nError no default available"
				self.actionLog.logRaw("Error no default available", self.now)
	
	# wait for current song to end
	def waitforend(self): 
		# control winamp as long as not in test mode 2
		if self.testing < 2:
			left = winampCtrl.timeleft()
			while left > 2:
				left = winampCtrl.timeleft()
			time.sleep(1)

	# print out all the properties of an event
	def printRawEvent(self, event):
		for e in event:
			t = e.tag
			print "~~~" + t + "~~~"
			if t != "default": 
				print e.get('name')
				print e.find('file').get('path')
				print e.find('day').get('code')
			if t == "show" or t == "playlist":
				print e.find('time').get('start')
				print e.find('time').get('end')
				print e.find('priority').text
			if t == "drop":
				print e.find('freq').text
			if t == "default": 
				for f in e.findall('file'): print f.get('path')
			print ""
			
	def printRawEvents(self):
		print "Current: "
		if self.currentShow != None: self.printRawEvent(self.currentShow)
		if self.currentPlaylist != None: self.printRawEvent(self.currentPlaylist)
		self.printRawEvent(self.currentDrops)
	
# convert times from xml object to time in minutes
def parseEventTime(event, key):
	# process event time info
	time = event.find('time').get(key)
	parts = time.split(":")
	return (int(parts[0]) * 60) + int(parts[1])