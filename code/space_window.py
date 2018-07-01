from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from urlparse import urlparse, parse_qs
import os
import signal
import threading
import subprocess
from time import sleep
from nasa_pod import NasaPod
from threading import Timer
import wifi_setup_ap.py_game_msg as msg
import wifi_setup_ap.wifi_control as wifi
import wifi_setup_ap.connection_http as connection
from mopidy_listener import MopidyUpdates
from html import get_main_html
import pygame
from streams import Streams
from async_job import Job

PORT_NUMBER = 80

_msg=msg.MsgScreen()
def status_update(txt):
    _msg.set_text(txt)


class WaitingMsgs:
    def __init__(self):
        self._msgs=['','this may take a little while...',
        '...still at it...','...working hard, have some respect...',
        '...do be patient...','...after all, this is a wonder of technology...',
        '...thank you for your patience :)...','...this is taking time, but...',
        '...few years ago you would have had to go to cinema for this...',
        '...admire the colors on the screen and wait...']
        self._current=0
        self.delay=10

    def _make_html(self,msg):
        body = u"""    
            <p style="font-size:35px">{}?</p>
        """.format(self.msg)
        return build_html(body,self.delay)
    
    def start(self):
        self._current=0
       
    def next(self,action_name=None):
        msg=self._msgs[self._current]
        self._current+=1
        if self._current >= len(self._msgs):
            self._current=0
        if action_name is not None:
            msg=action_name+'\n\n'+msg
        return msg

    def next_html(self,action_name=None):
        return self._make_html(self.next(action_name))    

_processes=None

#TODO:  REFRESH CACHES - TEST SPEED
#       TEST MOPIDY DOESN'T KILL SPEED
class ProcessHandling:
    def __init__(self,status_update_func):
        self._current_stream=None
        self._check_timer_delay=90
        self._check_timer=None
        self._wait=False
        self._streams=Streams.load()
        print 'STREAMS: ',self._streams
        self._nasa=NasaPod()
        threading.Thread(target=self.launch_mopidy).start()
        self._status_update=status_update_func    

    def launch_mopidy(self):
        subprocess.Popen(['mopidy'])
        self._mopidy=MopidyUpdates(status_update)
    
    def start_mopidy(self):
        if self._mopidy is not None:
            self._mopidy.show_updates()
        else:
            self._mopidy=MopidyUpdates(status_update)
            self._mopidy.show_updates()
            
    def streams(self):
        return self._streams
            
    def kill_running(self):
        print 'stopping running shows'
        self._status_update('stopping running shows')
        if self._check_timer is not None: 
            self.check_timer.cancel()
        self._streams.stop()
        self._nasa.stop()
        self._mopidy.stop()
        #wifi.run('pkill -9 mopidy')
       
    def wait(self):
        self._wait=True

    def stop_waiting(self):
        self._wait=False
 
    def play_stream(self,name):
        print 'starting stream %s' % name 
        if self._current_stream==name and _streams.is_playing():
            print 'stream %s is aready playing'
            return
        self.kill_running()   
        self._status_update('starting stream %s' % name)
        self._current_stream=name
        self._streams.play(name)

    def play_apod(self):
        print 'stopping streams'
        self._current_stream=None
        self._streams.stop()
        print 'playing apod'
        self._nasa.play()
     
    def play_next(self):
        if self._current_stream is None:
            name=self._streams.first()
        else:
            name=self._streams.next(current_stream) 
        if name is None: 
            print 'about to play apod'
            self.play_apod()
        else: 
            print 'about to play stream %s' % name
            self.play_stream(name)

    def run_something(self):
        if self._wait: return
        if self._check_timer is not None: self._check_timer.cancel()
        if not self._streams.is_playing():
            self.play_next()
        self._check_timer=Timer(self._check_timer_delay, self.run_something)
        self._check_timer.start()
        
    def handle_wifi_change_req(self,params,server):
        wifi_name='noname'
        password=None
        for n in params:
            v=params[n]
            if v==['Connect']:
                wifi_name=n
            elif n=='password':
                password=v[0]
        self._status_update('thanks! trying to connect to %s now' % wifi_name)
        wifi.set_wifi(wifi_name,password)
        wifi.restart_wifi()
        server.return_to_front()
        return True

    def refresh_caches(self):
        self._streams.refresh_caches(True)

_cnt=0 # global counter, used to make html more responsive
class SpaceWindowServer(BaseHTTPRequestHandler):
    def send_to(self,addr):
        self.send_response(301)
        self.send_header('Location',addr)
        self.end_headers()

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
    
    def return_to_front(self):
        self.send_to('/')
    
    def send_to_mopidy(self):
        ip=wifi.get_ip()
        self.send_to('http://%s:6680/radiorough' %ip)
    
    #Handler for the GET requests
    def do_GET(self):
        global _cnt
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
            self.return_to_front()
            return
        elif 'really_remove' in self.path:
            ps=params['action'][0]
            _streams.remove(ps[len('really remove '):])
            self.return_to_front()
            return
        elif 'add' in self.path:
            if params['name'][0] != 'NAME' and params['link'][0]!='LINK':
                name=params['name'][0].replace(' ','')
                _streams.add(params['name'][0],params['link'][0],
                    params['quality'][0])
            self.return_to_front()
            return
        elif 'slideshow' in self.path:
            _processes.play_apod()
            self.return_to_front()
            return
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
            self.return_to_front()
            status_update("changing wifi networks\nthis is a fragile process\ngive it a few minutes\nif it didn't work, reboot")
            _processes.handle_wifi_change_req(params,self)
            status_update('testing the new connection')
            if connection.test_connection():
                display_connection_details()
                sleep(20)
            _processes.stop_waiting()
            #check_running()
            return
        elif 'shutdown' in self.path:
            os.system('shutdown -h now')
            return
        elif 'kodi' in self.path:
            _processes.wait()
            _processes.kill_running()
            status_update('starting kodi')
            print 'starting kodi'
            os.system('sudo -u pi kodi-standalone')
            print 'started kodi'
            sleep(40)
            print 'slept a bit'
            ip=wifi.get_ip()
            txt='enjoy'
            print txt
            status_update(txt)
            self.return_to_front()
            _processes.stop_waiting()
            return
        elif 'rough' in self.path:
            #_processes.wait()
            #_processes.kill_running()
            #status_update('starting radio rough')
            #print 'starting mopidy'
            #subprocess.Popen(['mopidy'])
            #print 'started mopidy'
            #sleep(40)
            #print 'slept a bit'
            ip=wifi.get_ip()
            txt='go to spacewindow.local:6680/radiorough\nor %s:6680/radiorough' % ip
            print txt
            status_update(txt)
            self.send_to_mopidy()
            _processes.start_mopidy()
            #_processes.stop_waiting()            
            return
        elif 'next' in self.path:
            _processes.play_next()
            self.return_to_front()
            return
        elif 'refresh_caches' in self.path:
            _processes.refresh_caches()
        elif self.path.endswith('.jpg'):
            mimetype='image/jpg'
            #Open the static file requested and send it
            f = open('/home/pi/' + self.path) 
            self.send_response(200)
            self.send_header('Content-type',mimetype)
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
            return
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        # Send the html message
        html = get_main_html(_streams.make_html())
        self.wfile.write(html)

_server=None

def initialise_streams():
    global _processes
    _processes=ProcessHandling(status_update)
    return True   
 
def initialise_streams_timer():
    waiting_job=Job(initialise_streams)
    waiting_job.start()
       
    waiting_msg=WaitingMsgs()
    
    next_cnt=0
    while not waiting_job.done:
        if next_cnt==0:
            next_cnt=5
            status_update(waiting_msg.next('initialising streams'))
        next_cnt-=1
        sleep(1)

try:
    print 'configuring wifi'
    connection.configure_wifi(30,False)
    #Create a web server and define the handler to manage the
    #incoming request
    initialise_streams_timer()
    #status_update('getting streams information.\n'+\
    #    "do be patient, few years ago you'd have had to go to cinema for this" 
    #_processes=ProcessHandling(status_update)
    handler=SpaceWindowServer
    _server = HTTPServer(('', PORT_NUMBER),handler )
    print 'Started httpserver on port ' , PORT_NUMBER, _server.server_address
    connection.display_connection_details()
    sleep(10)
    _processes.run_something()    
    #Wait forever for incoming http requests
    _server.serve_forever()

except KeyboardInterrupt:
    print 'space window is shutting down'
    _processes.kill_running()
    if _server is not None:
        _server.socket.close()
finally:
    pygame.quit()
    
