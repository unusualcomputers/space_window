from __future__ import unicode_literals
from time import sleep
import connection_http as connection
import pygame
from server import wait_to_initialise,start_server,stop_server,set_standalone
import logger

_log=logger.get(__name__)

try:
    _log.info('hello :)')
    _log.info('configuring wifi')
    connected=connection.test_connection()
    #connection.configure_wifi(30,False)
    #Create a web server and define the handler to manage the
    #incoming request
    if connected:
        _log.info('connected')
        connection.display_connection_details()
        sleep(10)
    else:
        _log.info('starting ap')
        connection.start_ap()
    set_standalone(not connected)
    _log.info('waiting to initialise')
    wait_to_initialise()
    _log.info('initialised')
    #Wait forever for incoming http requests
    start_server()

except KeyboardInterrupt:
    _log.info('space window is shutting down')
except:
    _log.exception('uncaught exception in space window')
finally:
    stop_server()
    pygame.quit()
    
