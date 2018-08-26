from BaseHTTPServer import HTTPServer
from BaseHTTPServer import BaseHTTPRequestHandler
import ConfigParser
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
from config_util import Config
from shutil import copyfile

PORT_NUMBER = 80
MOPIDY_PORT=6680

_ip=wifi.get_ip()
_processes=None
_streams=None
_gallery=None
_server=None
_standalone=False

_log=logger.get(__name__)
_config = Config('space_window.conf',__file__)    

def set_standalone(standalone):
    global _standalone
    _standalone=standalone
    procmod.set_standalone(standalone)

_msg=msg.MsgScreen()
def _status_update(txt):
    _msg.set_text(txt)

def initialise_server():
    global _server
    #Wait forever for incoming http requests
    global _processes
    global _streams
    global _gallery
    if _processes is None:
        _processes=ProcessHandling(_status_update)
        _streams=_processes.streams()
        _gallery=_processes.gallery()
    handler=SpaceWindowServer
    _server = HTTPServer(('', PORT_NUMBER),handler )
    _log.info('Started httpserver on port %i',PORT_NUMBER)


def _update():
    this_path=os.path.dirname(os.path.abspath(__file__))
    old_path=os.path.join(this_path,'space_window.conf')
    new_path=os.path.join(this_path,'space_window.localconf')
   
    copyfile(old_path,new_path)
    os.system('git checkout -- %s' % old_path)
    os.system('git pull')
    parser = ConfigParser.SafeConfigParser()
    
    parser.read(old_path)
    parser.read(new_path)
    with open(old_path,'w') as cf:
        parser.write(cf)

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
    _processes.run_first_time()    
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
    _waiting_status(\
        'trying to connect to %s\nthis network is going down ' % wifi_name,
        wifi.set_wifi,(wifi_name,password))
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
    global _connecting_timer
    try:        
        _connecting_timer.cancel()
        params=_last_params
        _log.info('handling connect request %s' % params)
        _processes.pause()
        _status_update('changing wifi networks\n'+\
            'this is a fragile process\n'+\
            "give it a few minutes\nif it didn't work, reboot")
        _handle_start_wifi_req(params)
        set_standalone(False)
    finally:
        _connecting_timer=None
        _processes.resume()

def _upload_pic_job(server):
    try:
        _processes.pause() 
        sleep(1)
        chunk_size=128*1024
        _status_update('Uploading')
        total_size=int(server.headers['Content-Length'])
        form=server.get_post_form()
        p=os.path.join(os.path.dirname(os.path.abspath(__file__)),'photos')
        if not os.path.exists(p):
            os.makedirs(p)
        files = form['picture']
        if files is None or len(files)==0:
            return

        total_loaded=0
        percent=0
        not_uploaded=[]
        uploaded=[]
        for ff in files:
            filename=ff.filename
            picture_filename=os.path.join(p,filename.replace(' ','_'))
            with file(picture_filename, 'wb') as pictureout:
                picturein = ff.file 
                while True:
                    chunk = picturein.read(chunk_size)
                    total_loaded+= len(chunk)
                    percent=int(float(total_loaded)/total_size*100)
                    _status_update(\
                        'Uploading pictures\n%d percent' % percent)
                    if not chunk: break
                    pictureout.write(chunk)
            
            if not os.path.isfile(picture_filename):    
                not_uploaded.append(filename)
            else:
                uploaded.append(picture_filename)

        if not len(not_uploaded)==0:
            s=''.join(not_uploaded)
            s='Something went wrong, not all fies were uploaded :('
            _status_update(s)
            return
        _gallery.add_several(uploaded)
    finally:
        _processes.resume() 

class SpaceWindowServer(BaseHTTPRequestHandler):
    # send_to redirects to a different address
    def _respond(self,html):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(html)
    
    def _send_to(self,addr):
        self.send_response(301)
        self.send_header('Location',addr)
        self.end_headers()

        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
   
    def get_post_form(self):
        return cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
 
    def _upload_pic(self):
        _waiting_status('Uploading',_upload_pic_job,(self,))      
        self._send_to('/gallery?dummy=1')
    
    def _upload_video(self):
        try:
            _processes.pause() 
            chunk_size=128*1024
            _status_update('Uploading')
            total_size=int(self.headers['Content-Length'])
            form=self.get_post_form()
            p=os.path.join(os.path.dirname(os.path.abspath(__file__)),'videos')
            if not os.path.exists(p):
                os.makedirs(p)
            name = form['name'].value
            if len(name)==0 or name=='NAME':
                err='Sorry, you must tell me what to call this video'
                _status_update(err)
                self._respond(get_empty_html(err))
                sleep(5)
                _processes.resume() 
                return

            filename = form['video'].filename
            if len(filename)==0:
                err='Sorry, you must tell me a video file name'
                _status_update(err)
                self._respond(get_empty_html(err))
                sleep(5)
                _processes.resume() 
                return

            if len(form['subs'].filename)==0: file_cnt=1
            else: file_cnt=2
            
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
                self._respond(get_empty_html('Something went wrong, sorry :('))
                _status_update('Something went wrong, sorry :(')
                sleep(10)
                _processes.resume()
            else:
                _streams.add(name,video_filename,'default')
                self._send_to('/')
                _log.info('playing uploaded video')
                _processes.play_stream(name)
        except:
            _log.exception('Error while processing upload')
            _processes.resume()
                
    def do_POST(self):
        if 'upload' not in self.path:
            _log.error('Unknonw post request')
            self._send_to('/')
            return
        if 'upload_pic' in self.path:
            self._upload_pic()
        else:
            self._upload_video()
 
    #Handler for the GET requests
    def do_GET(self):
        try:
            params = parse_qs(urlparse(self.path).query)

            if 'play_remove?' in self.path:
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
            elif 'gallery?' in self.path:
                _processes.play_gallery()
                html=_gallery.make_html()
                self._respond(html)
                return     
            elif 'gallery_list?' in self.path:
                ps=params['action'][0]
                if 'picremove' in ps:
                    to_remove=[]
                    for p in params:
                        if 'remove_pic' in p:
                            to_remove.append(params[p][0])
                    
                    if len(to_remove)==0:
                        self._send_to('/gallery?dummy=1')
                        return
                    paths=','.join(to_remove)
                    html=_gallery.make_remove_html(paths)
                    self._respond(html)
                    return
                elif 'picup' in ps:
                    _processes.pause()
                    _status_update('Moving pictures, please wait')
                    sleep(2)
                    _gallery.move_up(ps[len('picup '):])
                    _processes.resume()
                else: 
                   raise Exception('Unknown request %s' % self.path)
                self._send_to('/gallery?dummy=1')
                return 
            elif 'really_remove_pic?' in self.path:
                _processes.pause()
                _status_update('Removing pictures, please wait')
                sleep(2)
                ps=params['action'][0]
                paths=ps[len('really remove '):].split(',')
                _gallery.remove_several(paths)
                self._send_to('/gallery?dummy=1')
                _processes.resume()
                return
            elif 'really_remove?' in self.path:
                ps=params['action'][0]
                _streams.remove(ps[len('really remove '):])
            elif 'config_change?' in self.path:
                ps=params['action'][0]
                global _msg
                if u'apply' in ps:
                    _config.parse_form_inputs(params)
                    _config.save()
                elif u'restore' in ps:
                    _config.restore_defaults()
                else:
                    _log.error('Unknown request for configuration %s' % params)
                _log.info('saved new config')
                _processes.pause()
                _log.info('updating msg screen')
                _msg=msg.MsgScreen()
                _log.info('init msg screen')
                _msg.init_once()
                _log.info('reloading conf')
                _processes.reload_config()
            elif 'next?' in self.path:
                _processes.play_next()
            elif 'refresh_caches?' in self.path:
                _processes.refresh_caches()
            elif 'add?' in self.path:
                if params['name'][0] != 'NAME' and params['link'][0]!='LINK':
                    name=params['name'][0].replace(' ','')
                    _streams.add(params['name'][0],params['link'][0],
                        params['quality'][0])
            elif 'clock?' in self.path:
                _processes.play_clock()
            elif 'slideshow?' in self.path:
                _processes.play_nasa()
            elif 'upload?' in self.path:
                html = get_upload_html() 
                self._respond(html)
                return
            elif 'update_sw?' in self.path:
                _processes.pause()
                _status_update('Downloading updated fies\n' +\
                    'Updates will happen when you reboot next')
                _update()
                _status_update('Updated fies\n' +\
                    'Updates will happen when you reboot next')
                sleep(10)
                _processes.resume()
            elif 'configuration?' in self.path:
                html = _config.get_html()
                self._respond(get_empty_html(html))
                return
            elif 'wifi?' in self.path:
                html = connection.make_wifi_html() 
                self._respond(html)
                return
            elif 'connect?' in self.path:
                global _last_params
                global _connecting_timer
                if _connecting_timer is None:
                    _last_params=params
                    _connecting_timer=Timer(5, _handle_connect_request)
                    _connecting_timer.start()
                    html='<h2>Now trying to connect to new network.<br>'+\
                        'This network will go down.<br>'+\
                        'Please follow instructions on your space window.</h2>'
                    self._respond(get_empty_html(html))
                    return
                else:
                    html='<h2>Already trying to connect to a network.<br>'+\
                        'Please be patient and<br>'+\
                        'follow instructions on your space window.</h2>'
                    self._respond(get_empty_html(html))
                    return
            elif 'scan?' in self.path:
                html = connection.make_wifi_html() 
                self._respond(html)
                return
            elif 'reboot?' in self.path:
                _status_update('rebooting in a few seconds, see you soon :)')
                Timer(5,_reboot).start()
            elif 'shutdown?' in self.path:
                _status_update('shutting down in a few seconds, goodbye :)')
                Timer(5,_shutdown).start()
            elif 'kodi?' in self.path:
                _processes.wait()
                _processes.kill_running()
                _status_update('starting kodi')
                _log.info('starting kodi')
                os.system('sudo -u pi kodi-standalone')
                _log.info('started kodi')
                txt='enjoy'
                _status_update(txt)
                _processes.stop_waiting()
            elif 'rough?' in self.path:
                self._send_to('http://%s:%i' % (_ip,MOPIDY_PORT))
                return
            elif self.path != '/' and _gallery.is_pic(self.path):
                pic=_gallery.serve_pic(self.path)
                mimetype='image/jpg'
                #Open the static file requested and send it
                self.send_response(200)
                self.send_header('Content-type',mimetype)
                self.end_headers()
                self.wfile.write(pic)
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
