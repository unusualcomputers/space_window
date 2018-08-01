from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
from urlparse import urlparse, parse_qs
import os
from time import sleep
import wifi_setup_ap.wifi_control as wifi
import wifi_setup_ap.connection_http as connection
from html import get_main_html
import wifi_setup_ap.py_game_msg as msg
import logger
from processes import *
from async_job import Job
from waiting_messages import WaitingMsgs
from threading import Timer

PORT_NUMBER = 80
MOPIDY_PORT=6680

_ip=wifi.get_ip()
_processes=None
_streams=None
_server=None



_msg=msg.MsgScreen()
def _status_update(txt):
    log=logger.get(__name__)
    log.info(txt)
    _msg.set_text(txt)

def _initialise_streams():
    global _processes
    global _streams
    if _processes is None:
        _processes=ProcessHandling(_status_update)
        _streams=_processes.streams()

def initialise_server():
    global _server
    handler=SpaceWindowServer
    _server = HTTPServer(('', PORT_NUMBER),handler )
    log=logger.get(__name__)
    log.info('Started httpserver on port %i',PORT_NUMBER)
    _initialise_streams()

def wait_to_initialise():
    waiting_job=Job(initialise_server)
    waiting_job.start()
       
    waiting_msg=WaitingMsgs()
    
    next_cnt=0
    while not waiting_job.done:
        if next_cnt==0:
            next_cnt=5
            _status_update(waiting_msg.next('initialising streams'))
        next_cnt-=1
        sleep(1)
    return waiting_job.result

def start_server():
    #Wait forever for incoming http requests
    _processes.run_something()    
    _server.serve_forever()

def stop_server():
    if _processes is not None:
        _processes.kill_running(False)
    if _server is not None:
        _server.socket.close()

def _shutdown():
    os.system('shutdown -h now')

def _reboot():
    os.system('reboot now')

class SpaceWindowServer(BaseHTTPRequestHandler):
    # send_to redirects to a different address
    def _send_to(self,addr):
        self.send_response(301)
        self.send_header('Location',addr)
        self.end_headers()

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
    
    #Handler for the GET requests
    def do_GET(self):
        _initialise_streams()
        log=logger.get(__name__)
        params = parse_qs(urlparse(self.path).query)

        if 'play_remove' in self.path:
            ps=params['action'][0]
            if u'remove' in ps:
                html=_streams.make_remove_html(ps[len('remove '):])
                self.wfile.write(html)
                return
            elif 'moveup' in ps:
                _streams.up(ps[len('moveup '):])
            else: #if it's not remove, then it's play
                _processes.play_stream(ps[len('play '):])
                _processes.run_something()
        elif 'really_remove' in self.path:
            ps=params['action'][0]
            _streams.remove(ps[len('really remove '):])
        elif 'next' in self.path:
            _processes.play_next()
        elif 'refresh_caches' in self.path:
            _processes.refresh_caches()
        elif 'add' in self.path:
            if params['name'][0] != 'NAME' and params['link'][0]!='LINK':
                name=params['name'][0].replace(' ','')
                _streams.add(params['name'][0],params['link'][0],
                    params['quality'][0])
        elif 'slideshow' in self.path:
            _processes.play_apod()
        elif 'wifi' in self.path:
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            # Send the html message
            html = connection.make_wifi_html() 
            self.wfile.write(html)
            return
        elif 'connect' in self.path:
            _processes.wait()
            _processes.kill_running()
            _status_update('changing wifi networks\n'+\
                'this is a fragile process\n'+\
                "give it a few minutes\nif it didn't work, reboot")
            _processes.handle_wifi_change_req(params,self)
            _status_update('testing the new connection')
            if connection.test_connection():
                display_connection_details()
                sleep(20)
            _processes.stop_waiting()
            #check_running()
        elif 'reboot' in self.path:
            _status_update('rebooting in a few seconds, see you soon :)')
            Timer(5,_reboot).start()
        elif 'shutdown' in self.path:
            _status_update('shutting down in a few seconds, goodbye :)')
            Timer(5,_shutdown).start()
        elif 'kodi' in self.path:
            _processes.wait()
            _processes.kill_running()
            _status_update('starting kodi')
            log.info('starting kodi')
            os.system('sudo -u pi kodi-standalone')
            log.info('started kodi')
            txt='enjoy'
            _status_update(txt)
            _processes.stop_waiting()
        elif 'rough' in self.path:
            #_processes.wait()
            #_processes.kill_running()
            #_status_update('starting radio rough')
            #print 'starting mopidy'
            #subprocess.Popen(['mopidy'])
            #print 'started mopidy'
            #sleep(40)
            #print 'slept a bit'
            txt='mopidy is starting'
            log.info(txt)
            #_status_update(txt)
            self._send_to('http://%s:%i' % (_ip,MOPIDY_PORT))
            _processes.start_mopidy()
            #_processes.stop_waiting()            
            return
        elif self.path.endswith('.jpg'):
            # getting pictures for backgrounds and such
            mimetype='image/jpg'
            #Open the static file requested and send it
            f = open('/home/pi/' + self.path) 
            self.send_response(200)
            self.send_header('Content-type',mimetype)
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
            return
        else:
            # front page
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            # Send the html message
            html = get_main_html(_streams.make_html())
            self.wfile.write(html)
            return
        # everything that is not changing the address is sent back to start
        self._send_to('/')

