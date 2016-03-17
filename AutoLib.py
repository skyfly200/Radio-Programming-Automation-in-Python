import clever as winampCtrl
import xml.etree.ElementTree as xmlProcessor
import os.path, re, random, time, win32api
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
		# sync the time object to the current time
		time.sync()
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
			log = f.readlines()[-1]
		return log
	
	# return the timestamp of the last log in the log file
	def lastLogTime(self):
		timestamp = False
		with open(self.logPath) as f:
			timestamp = f.readlines()[-2][:-3]
		return timestamp

	# check if last event has ended
	def over(self, logLine=''):
		if logLine == '': 
			logLine = self.lastLog()
		logLine = str(logLine)
		
		# if last log was a show or playlist
		if logLine[:4] == "show" or logLine[:8] == "playlist":
			endTime = (logLine[-5:-4] * 60) + logLine[-2:]
			print endTime
			if endTime > timeTotM: return True
			else: return False
			
		# if last log was a drop
		elif logLine[:4] == "drop": 
			return True
			
		# if last log was default
		elif logLine[:7] == "default": 
			return False
		
		# return true by default
		else: return True
	
		# One-line file.
		return suffix

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
		listEx = re.compile(r'([0-9a-z/]{3,9}, ?)+[0-9a-z/]{3,9}', re.IGNORECASE)
		todayEx = re.compile(r'\A' + self.dayStr + '[a-z]*', re.IGNORECASE)
		
		# if code matched todays weekday
		if todayEx.match(dayCode):
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
		# parse the xml file
		root = self.parseXML(xmlFile)
		# Look for events in the schedule xml structure
		self.shows = root.findall('show')
		self.playlists = root.findall('playlist')
		self.drops = root.findall('drop')
		self.defaults = root.findall('default')
		# initialize lists for current events
		self.currentShow = None
		self.currentPlaylist = None
		self.currentDrops = []
		# create a datetime object for checking the current time
		self.now = datetime()
		# create new log objects to log actions and errors
		self.actionLog = log("autoLog.txt", "Automation Actions")
		self.errorLog = log("errorLog.txt", "Automation Errors")
		# number of minutes to start a show early 
		self.earlyStart = 1

	# update the schedule object with provided xml file
	def update(self, xmlFile):
		# parse the xml file
		root = self.parseXML(xmlFile)
		# Look for events in the schedule xml structure
		self.shows = root.findall('show')
		self.playlists = root.findall('playlist')
		self.drops = root.findall('drop')
		self.defaults = root.findall('default')

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
		# Check for current show
		for show in self.shows:
			# process shows time info
			day = show.find('day').get('code')
			start = show.find('time').get('start')
			end = show.find('time').get('end')
			startParts = start.split(":")
			endParts= end.split(":")
			startMinute = (int(startParts[0]) * 60) + int(startParts[1]) - self.earlyStart
			endMinute = (int(endParts[0]) * 60) + int(endParts[1])
			# sync the time object to the current time
			self.now.sync()
			# check show date and time agianst current date and time  
			if self.now.getInMinutes() >= startMinute and self.now.getInMinutes() < endMinute and self.now.checkDay(day):
				# check show priority	
				showPriority = int(show.find('priority').text)
				if showPriority < priority:
					newEvent = True
					self.currentShow = show
			
			
		# Check for current playlist
		priority = 100
		for playlist in self.playlists:
			# process shows time info
			day = playlist.find('day').get('code')
			start = playlist.find('time').get('start')
			end = playlist.find('time').get('end')
			startParts = start.split(":")
			endParts= end.split(":")
			startMinute = (int(startParts[0]) * 60) + int(startParts[1])
			endMinute = (int(endParts[0]) * 60) + int(endParts[1])
			# sync the time object to the current time
			self.now.sync()
			# check showplaylist date and time agianst current date and time  
			if self.now.getInMinutes() >= startMinute and self.now.getInMinutes() < endMinute and self.now.checkDay(day):
				# check playlist priority	
				playlistPriority = int(playlist.find('priority').text)
				if playlistPriority < priority:
					priority = playlistPriority
					self.currentPlaylist = playlist
					newEvent = True
					
		
		# Check for current drops
		for drop in self.drops:
			# process drop playback info
			freq = drop.find('freq').text
			code = drop.find('day').get('code')
			# sync the time object to the current time
			self.now.sync()
			# check drop date agianst current date
			if (self.now.getInMinutes() % int(freq)) == 0 and self.now.checkDay(code):
				self.currentDrops.append(drop)
				newEvent = True
		
		# return if there are any new events to run
		return newEvent
				
			
	def playCurrentEvent(self):
		
		# set default priority and event
		priority = 100
		
		idleWait = 30 # seconds to wait for idle before running playlists or drops
		
		# if there is a scheduled show, check if show is not already playing, then play it
		if self.currentShow is not None:
			if self.actionLog.lastLog() != self.actionLog.makeLog(self.currentShow, ""):
				print "Show: ", self.currentShow.get('name'), "\nTime Slot:", self.currentShow.find('time').get('start'), "-", self.currentShow.find('time').get('end')
				# if playing something then fade out
				if winampCtrl.status() == 1:
					winampCtrl.fadeOut()
				# play show, fade in and log the show
				winampCtrl.loadplay(self.currentShow.find('file').get('path'))
				winampCtrl.volmax()
				self.actionLog.logAction(self.currentShow, self.now)
			
		# if there are no current shows, the computer is idle and winamp is playing, then look for other current events
		elif winampCtrl.status() == 1 and get_idle_duration() >= idleWait:
			# check if there are any current drops to play
			if len(self.currentDrops) > 0:
				# if playing a song wait for current song to end
				# skips if playing a stream
				timeLeft = winampCtrl.timeleft()
				if timeLeft > 0: time.sleep(timeLeft - 1)
				for drop in self.currentDrops:
					# make sure shuffle is on
					if winampCtrl.getshuffle() == 0: 
						winampCtrl.swshuffle()
					# load the drop
					winampCtrl.loadplay(drop.find('file').get('path'))
					# print drop info and log the event
					print "\nDrop: " + drop.get('name'), " Frequency: ", drop.find('freq').text, "Min"
					self.actionLog.logAction(drop, self.now)
					# wait for song to end before continuing
					time.sleep(winampCtrl.timeleft() - 1)
					
			# if there is a current playlist make sure its not already playing
			if self.currentPlaylist is not None and self.actionLog.lastLog() != self.actionLog.makeLog(self.currentPlaylist, ""):
				# make sure shuffle is on
				if winampCtrl.getshuffle() == 0: winampCtrl.swshuffle()
				print "\nPlaylist: " + self.currentPlaylist.get('name'), "\nTime Slot:", self.currentPlaylist.find('time').get('start'), "-", self.currentPlaylist.find('time').get('end')
				winampCtrl.loadplay(self.currentPlaylist.find('file').get('path'))
				self.actionLog.logAction(self.currentPlaylist, self.now)
			# if no playlist or show then goto the default
			elif self.currentPlaylist is None and self.currentShow is None:
				self.gotoDefault()
		
	# when no playlist or show is scheduled and there are defaults, then randomly load one
	def gotoDefault(self):
			if (len(self.defaults) > 0): 
				# randomly choose a default from the list
				default = random.choice(self.defaults)
				path = str(default.find('file').get('path'))
				if self.actionLog.lastLog() != self.actionLog.makeLog(default, path):
					print "\nGoing to default - ", path
					self.actionLog.logAction(default, self.now, path)
					winampCtrl.loadplay(path)
			else:
				print "\nError no default available"
				self.actionLog.logRaw("Error no default available", self.now)
	
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
	