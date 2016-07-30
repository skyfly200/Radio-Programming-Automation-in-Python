import os, subprocess
os.system("taskkill /im cmd.exe /f")
subprocess.call('Automation.py', shell=True)
