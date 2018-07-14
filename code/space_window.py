from time import sleep
import wifi_setup_ap.connection_http as connection
import pygame
from async_job import Job
from waiting_messages import WaitingMsgs
from server import initialise_server,start_server,stop_server
import logger

#TODO:  REFRESH CACHES - TEST SPEED
#       TEST MOPIDY DOESN'T KILL SPEED


log=logger.get(__name__)

_msg=msg.MsgScreen()
def status_update(txt):
    log.info(txt)
    _msg.set_text(txt)

def wait_to_initialise():
    waiting_job=Job(initialise_server)
    waiting_job.start()
       
    waiting_msg=WaitingMsgs()
    
    next_cnt=0
    while not waiting_job.done:
        if next_cnt==0:
            next_cnt=5
            status_update(waiting_msg.next('initialising streams'))
        next_cnt-=1
        sleep(1)
    return waiting_job.result

try:
    log.info('configuring wifi')
    connection.configure_wifi(30,False)
    #Create a web server and define the handler to manage the
    #incoming request
    wait_to_initialise()
    connection.display_connection_details()
    sleep(10)
    #Wait forever for incoming http requests
    start_server()

except KeyboardInterrupt:
    log.info('space window is shutting down')
except:
    log.exception('uncaught exception in space window')
finally:
    pygame.quit()
    stop_server()
    
