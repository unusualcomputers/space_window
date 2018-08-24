from time import sleep
import connection_http as connection
import pygame
from server import wait_to_initialise,start_server,stop_server,set_standalone
import logger

log=logger.get(__name__)

try:
    log.info('hello :)')
    log.info('configuring wifi')
    connected=connection.test_connection()
    #connection.configure_wifi(30,False)
    #Create a web server and define the handler to manage the
    #incoming request
    if connected:
        log.info('connected')
        connection.display_connection_details()
        sleep(10)
    else:
        log.info('starting ap')
        connection.start_ap()
    set_standalone(not connected)
    log.info('wiating to initialise')
    wait_to_initialise()
    log.info('initialised')
    #Wait forever for incoming http requests
    start_server()

except KeyboardInterrupt:
    log.info('space window is shutting down')
except:
    log.exception('uncaught exception in space window')
finally:
    pygame.quit()
    stop_server()
    
