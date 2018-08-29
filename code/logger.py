from __future__ import unicode_literals
import logging
import sys
loggers={}
logfrmt='%(levelname)s - %(asctime)s:%(msecs)d - %(name)s: %(message)s'
formatter=logging.Formatter(logfrmt,'%H:%M:%S')
lvl=logging.DEBUG
console = logging.StreamHandler(sys.stdout)
console.setLevel(lvl)
console.setFormatter(formatter)
rootLog='SpaceWindow'
#filelogger=logging.FileHandler('/home/pi/space_window/code/space_window.log')
#filelogger.setFormatter(formatter)
def get(subname):
    global loggers
    name='%s.%s' %(rootLog,subname)
    if name in loggers: return loggers[name]
    l=logging.getLogger(name)
    l.handlers = []
    l.addHandler(console) 
    #l.addHandler(filelogger)
    l.setLevel(lvl)
    loggers[name]=l
    return l
