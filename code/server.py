from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
from urlparse import urlparse, parse_qs
import os
from time import sleep
import wifi_control as wifi
import connection_http as connection
from html import * 
import py_game_msg as msg
import logger
from processes import *
import processes as procmod
from async_job import Job
from waiting_messages import WaitingMsgs
from threading import Timer,Thread
import cgi
import streams

PORT_NUMBER = 80
MOPIDY_PORT=6680

_ip=wifi.get_ip()
_processes=None
_streams=None
_server=None
_standalone=False

_log=logger.get(__name__)

def set_standalone(standalone):
    global _standalone
    _standalone=standalone
    procmod.set_standalone(standalone)

_msg=msg.MsgScreen()
def _status_update(txt):
    _log.info(txt)
    _msg.set_text(txt)

def _initialise_streams():
    global _processes
    global _streams
    if _processes is None:
        _processes=ProcessHandling(_status_update)
        _streams=_processes.streams()

def initialise_server():
    global _server
    #Wait forever for incoming http requests
    handler=SpaceWindowServer
    _server = HTTPServer(('', PORT_NUMBER),handler )
    _log.info('Started httpserver on port %i',PORT_NUMBER)
    _initialise_streams()


def _waiting_status(msg, job, args=None):
    waiting_job=Job(job,args)
    waiting_job.start()
       
    waiting_msg=msg+'\n'
    
    while not waiting_job.done:
        _status_update(waiting_msg)
        sleep(1)
        waiting_msg+='.'
    return waiting_job.result

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
    _processes.run_something()    
    _server.serve_forever()

def stop_server():
    if _processes is not None:
        _processes.kill_running()
    if _server is not None:
        _server.socket.close()

def _shutdown():
    os.system('shutdown -h now')

def _reboot():
    os.system('reboot now')

def _handle_start_wifi_req(params):
    wifi_name='noname'
    password=None
    for n in params:
        v=params[n]
        if v==['connect']:
            wifi_name=n
        elif n=='password':
            password=v[0]
    #_status_update('trying to connect to %s now\n' % wifi_name)
    _waiting_status(\
        'trying to connect to %s\nthis network is going down ' % wifi_name,
        wifi.set_wifi,(wifi_name,password))
    #server.wfile.write(make_attempting_html())
    #wifi.set_wifi(wifi_name,password)
    #_status_update('restarting wifi')
    _waiting_status('restarting wifi',wifi.start_wifi)
    _status_update('testing the new connection')
    if connection.test_connection():
        connection.display_connection_details()
        sleep(10)
        return True

    _status_update\
        ('can\'t connect to wifi :(\nbringing access point up again')
    wifi.start_ap()
    return False

_last_params=None
_connecting_timer=None
def _handle_connect_request():
    try:        
        _connecting_timer.cancel()
        params=_last_params
        _log.info('handling connect request %s' % params)
        _processes.wait()
        _processes.kill_running(True)
        _status_update('changing wifi networks\n'+\
            'this is a fragile process\n'+\
            "give it a few minutes\nif it didn't work, reboot")
        _handle_start_wifi_req(params)
        set_standalone(False)
        _processes.stop_waiting()
        _processes.run_something()
    finally:
        global _connecting_timer
        _connecting_timer=None

class SpaceWindowServer(BaseHTTPRequestHandler):
    # send_to redirects to a different address
    def _respond(self,html):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        # Send the html message
        self.wfile.write(html)
    
    def _send_to(self,addr):
        self.send_response(301)
        self.send_header('Location',addr)
        self.end_headers()

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
    
    def _handle_wifi_change_req(self,params):
        wifi_name='noname'
        password=None
        _log.info('wifi connection params ' + str(params)) 
        for n in params:
            v=params[n]
            if v==['connect']:
                wifi_name=n
            elif n=='password':
                password=v[0]
        _status_update('trying to connect to %s now' % wifi_name)
        wifi.set_wifi(wifi_name,password)
        wifi.restart_wifi()
        self._send_to('/')
        return True


    def do_POST(self):
        try:
            _processes.kill_running() 
            if 'upload' not in self.path:
                _log.error('Unknonw post request')
                self._send_to('/')
            chunk_size=128*1024
            _status_update('Getting info about files to upload')
            total_size=int(self.headers['Content-Length'])
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD':'POST',
                         'CONTENT_TYPE':self.headers['Content-Type'],
                         })
            p=os.path.join(os.path.dirname(os.path.abspath(__file__)),'videos')
            if not os.path.exists(p):
                os.makedirs(p)
            name = form['name'].value
            if len(name)==0 or name=='NAME':
                err='Sorry, you must tell me what to call this video'
                _status_update(err)
                self._respond(get_error_html(err))
                sleep(5)
                return

            filename = form['video'].filename
            if len(filename)==0:
                err='Sorry, you must tell me a video a file name'
                _status_update(err)
                self._respond(get_error_html(err))
                sleep(5)
                return

            if len(form['subs'].filename)==0: file_cnt=1
            else: file_cnt=2
            
            chunk_percent=float(chunk_size)/total_size
            total_loaded=0
            percent=0
            video_filename=os.path.join(p,filename.replace(' ','_'))
            with file(video_filename, 'wb') as videoout:
                videoin = form['video'].file
                while True:
                    chunk = videoin.read(chunk_size)
                    total_loaded+= len(chunk)
                    percent=int(float(total_loaded)/total_size*100)
                    _status_update(\
                        'Uploading video file\n%d percent' % percent)
                    if not chunk: break
                    videoout.write(chunk)
            
            _status_update('Uploaded video file')
            if file_cnt==2: 
                subsname=os.path.splitext(filename)[0].replace(' ','_')+'.srt'
                with file(os.path.join(p,subsname), 'wb') as subsout:
                    subsin = form['subs'].file
                    while True:
                        chunk = subsin.read(chunk_size)
                        total_loaded+= len(chunk)
                        percent=int(float(total_loaded)/total_size*100)
                        _status_update(\
                            'Uploading subtitles\n%d percent' % percent)
                        if not chunk: break
                        subsout.write(chunk)
            if not os.path.isfile(video_filename):    
                self._respond(get_error_html('Something went wrong, sorry :('))
                _status_update('Something went wrong, sorry :(')
                sleep(10)
            else:
                _streams.add(name,video_filename,'default')
                self._send_to('/')
                _log.info('playing uploaded video')
                _processes.play_stream(name)
        except:
            _log.exception('Error while processing upload')
            _processes.run_something()
    
    #Handler for the GET requests
    def do_GET(self):
        try:
            _initialise_streams()
            params = parse_qs(urlparse(self.path).query)

            if 'play_remove' in self.path:
                ps=params['action'][0]
                if u'remove' in ps:
                    html=_streams.make_remove_html(ps[len('remove '):])
                    self._respond(html)
                    return
                elif 'moveup' in ps:
                    _streams.up(ps[len('moveup '):])
                else: #if it's not remove, then it's play
                    _log.info('playing as requested')
                    _processes.play_stream(ps[len('play '):])
                    #_processes.run_something()
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
            elif 'clock' in self.path:
                _processes.play_clock()
            elif 'slideshow' in self.path:
                _processes.play_apod()
            elif 'upload' in self.path:
                html = get_upload_html() 
                self._respond(html)
                return
            elif 'wifi' in self.path:
                html = connection.make_wifi_html() 
                self._respond(html)
                return
            elif 'connect' in self.path:
                global _last_params
                global _connecting_timer
                if _connecting_timer is None:
                    _last_params=params
                    _connecting_timer=Timer(5, _handle_connect_request)
                    _connecting_timer.start()
                    html='<h2>Now trying to connect to new network.<br>'+\
                        'This network will go down.<br>'+\
                        'Please follow instructions on your space window.</h2>'
                    self._respond(get_error_html(html))
                    return
                else:
                    html='<h2>Already trying to connect to a network.<br>'+\
                        'Please be patient and<br>'+\
                        'follow instructions on your space window.</h2>'
                    self._respond(get_error_html(html))
                    return

            elif 'scan' in self.path:
                html = connection.make_wifi_html() 
                self._respond(html)
                return
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
                _log.info('starting kodi')
                os.system('sudo -u pi kodi-standalone')
                _log.info('started kodi')
                txt='enjoy'
                _status_update(txt)
                _processes.stop_waiting()
            elif 'rough' in self.path:
                self._send_to('http://%s:%i' % (_ip,MOPIDY_PORT))
                _processes.start_mopidy()
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
                if _standalone:
                    html = get_standalone_html(_streams.make_html())
                else:
                    html = get_main_html(_streams.make_html())
                self._respond(html)
                return
            # everything that is not changing the address is sent back to start
            self._send_to('/')
        except:
            _log.exception('Error while dealing with server request')
            raise
