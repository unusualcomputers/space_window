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
#logging.basicConfig(format=logfrmt,level=lvl)
def get(subname):
    global loggers
    name='%s.%s' %(rootLog,subname)
    if name in loggers: return loggers[name]
    
    l=logging.getLogger(name)
    l.handlers = []
    l.addHandler(console) 
    l.setLevel(lvl)
    loggers[name]=l
    return l
