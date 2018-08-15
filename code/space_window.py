from time import sleep
import connection_http as connection
import pygame
from server import wait_to_initialise,start_server,stop_server
import logger

log=logger.get(__name__)

try:
    log.info('hello :)')
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
    
