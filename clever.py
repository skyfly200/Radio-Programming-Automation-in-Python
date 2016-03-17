import sys, string, os
import subprocess

def playpause():
	return subprocess.subprocess.call('clever.exe playpause', shell=True)
	
def play():
	return subprocess.call('clever.exe play', shell=True)

def pause():
	return subprocess.call('clever.exe pause', shell=True)

def stop():
	return subprocess.call('clever.exe stop', shell=True)

def prev():
	return subprocess.call('clever.exe prev', shell=True)

def next():
	return subprocess.call('clever.exe next', shell=True)

def rewind():
	return subprocess.call('clever.exe rewind', shell=True)

def forward():
	return subprocess.call('clever.exe forward', shell=True)

def load(filename):
	return subprocess.call(['clever.exe', 'load', '%s' % filename], shell=True)

def loadnew(filename):
	return subprocess.call(['clever.exe', 'loadnew', '%s' % filename], shell=True)

def loadplay(filename):
	return subprocess.call(['clever.exe', 'loadplay', '%s' % filename], shell=True)

def volup():
	return subprocess.call('clever.exe volup', shell=True)

def voldn():
	return subprocess.call('clever.exe voldn', shell=True)

def volume(v):
	return subprocess.call(['clever.exe', 'volume', '%s' % v], shell=True)
	
def mute():
	return volume(0)
	
def volmax():
	return volume(255)
	
def fadeOut():
	i = 255
	r = 16
	while i > 0: 
		i -= r
		if i < 0: i = 0
		volume(i)
	
def fadeIn():
	i = 0
	r = 16
	while i < 255: 
		i += r
		if i > 255: i = 255
		volume(i)
	
def clear():
	return subprocess.call('clever.exe clear', shell=True)

def status():
	return subprocess.call('clever.exe status', shell=True)
	
def getplpos():
	return subprocess.call('clever.exe getplpos', shell=True)
	
def swshuffle():
	return subprocess.call('clever.exe swshuffle', shell=True)
	
def swrepeat():
	return subprocess.call('clever.exe swrepeat', shell=True)
	
def getshuffle():
	return subprocess.call('clever.exe getshuffle', shell=True)
	
def getrepeat():
	return subprocess.call('clever.exe getrepeat', shell=True)
	
def position():
	return subprocess.call('clever.exe position', shell=True)
	
def timeleft():
	return subprocess.call('clever.exe timeleft', shell=True)
	
def songlength():
	return subprocess.call('clever.exe songlength', shell=True)
