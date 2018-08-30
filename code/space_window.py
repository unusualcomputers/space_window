import pg_init
_screen=pg_init.screen()
from __future__ import unicode_literals
from time import sleep
import connection_http as connection
import pygame
from server import *
set_screen(_screen)
_status_update=get_status_update_func()
import logger
_log=logger.get(__name__)

try:
    _log.info('hello :)')
    _log.info('configuring wifi')
    connection.set_reporting_func(_status_update)
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
    
