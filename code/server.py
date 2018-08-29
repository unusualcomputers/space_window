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
import random

PORT_NUMBER = 80
MOPIDY_PORT=6680

_ip=wifi.get_ip()
_processes=None
_streams=None
_gallery=None
_music=None
_server=None
_standalone=False
_cnt=random.randint(0,1000)

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
    global _music
    if _processes is None:
        _processes=ProcessHandling(_status_update)
        _streams=_processes.streams()
        _gallery=_processes.gallery()
        _music=_processes.music()
    handler=SpaceWindowServer
    _server = HTTPServer(('', PORT_NUMBER),handler )
    _log.info('Started httpserver on port %i',PORT_NUMBER)


def _update():
    this_path=os.path.dirname(os.path.abspath(__file__))
    old_path=os.path.join(this_path,'space_window.conf')
    new_path=os.path.join(this_path,'space_window.localconf')
   
    copyfile(old_path,new_path)
    os.system('cd %s;git checkout -- %s' % (this_path,old_path))
    os.system('cd %s;git pull' % this_path)
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
    os.system('pkill -9 python')

def _reboot():
    os.system('reboot now')
    os.system('pkill -9 python')

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
    connection.start_ap()
    return False

_last_params=None
_connecting_timer=None
def _handle_connect_request():
    global _connecting_timer
    global _ip
    
    try:        
        _connecting_timer.cancel()
        params=_last_params
        _log.info('handling connect request %s' % params)
        _processes.pause()
        _status_update('changing wifi networks\n'+\
            'this is a fragile process\n'+\
            "give it a few minutes\nif it didn't work, reboot")
        if _handle_start_wifi_req(params):
            set_standalone(False)
    finally:
        _ip=wifi.get_ip()
        _connecting_timer=None
        _processes.resume()

def _free_disk_space():
    stat=os.statvfs('/')
    return stat.f_bfree * stat.f_frsize

def _upload_video_job(server):
    try:
        _processes.pause() 
        chunk_size=128*1024
        total_size=int(server.headers['Content-Length'])
        if (total_size * 5) > _free_disk_space():
            return 'Not enough disk splace left'
        form=server.get_post_form()
        p=os.path.join(os.path.dirname(os.path.abspath(__file__)),'videos')
        if not os.path.exists(p):
            os.makedirs(p)
        name = form['name'].value
        if len(name)==0 or name=='NAME':
            return 'Videos must have names'

        filename = form['video'].filename
        if len(filename)==0:
            return 'Erm, you did not give me a file'

        if len(form['subs'].filename)==0: file_cnt=1
        else: file_cnt=2
        
        total_loaded=0
        video_filename=os.path.join(p,filename.replace(' ','_'))
        with file(video_filename, 'wb') as videoout:
            videoin = form['video'].file
            while True:
                chunk = videoin.read(chunk_size)
                total_loaded+= len(chunk)
                if not chunk: break
                videoout.write(chunk)
        
        if file_cnt==2: 
            subsname=os.path.splitext(filename)[0].replace(' ','_')+'.srt'
            with file(os.path.join(p,subsname), 'wb') as subsout:
                subsin = form['subs'].file
                while True:
                    chunk = subsin.read(chunk_size)
                    total_loaded+= len(chunk)
                    if not chunk: break
                    subsout.write(chunk)
        
        if not os.path.isfile(video_filename):    
            _status_update('Something went wrong, sorry :(')
            sleep(10)
            _processes.resume()
            return 'File not saved for some reason'
        else:
            _streams.add(name,video_filename,'default')
            server._send_to('/')
            _log.info('playing uploaded video')
            _processes.play_stream(name)
            return ''
    except:
        _log.exception('Error while processing upload')
        _processes.resume()
        return 'There was an exception, cehck the logs'

def _upload_music_job(server):
    try:
        chunk_size=128*1024
        total_size=int(server.headers['Content-Length'])
        if (total_size * 5) > _free_disk_space():
            return 'Not enough disk splace left'
        form=server.get_post_form()
        p=os.path.join(os.path.dirname(os.path.abspath(__file__)),'music')
        foldername = form['foldername'].value
        p=os.path.join(p,foldername)
        if not os.path.exists(p):
            os.makedirs(p)
        files = form['music']
        if files is None or len(files)==0:
            return 'Erm, you did not give me a file'

        total_loaded=0
        not_uploaded=[]
        uploaded=[]
        for ff in files:
            filename=ff.filename
            music_filename=os.path.join(p,filename)
            with _music.lock():
                with file(music_filename, 'wb') as musicout:
                    musicin = ff.file 
                    while True:
                        chunk = musicin.read(chunk_size)
                        total_loaded+= len(chunk)
                        if not chunk: break
                        musicout.write(chunk)
                
                if not os.path.isfile(music_filename):    
                    not_uploaded.append(filename)
                else:
                    uploaded.append(music_filename)

        if not len(not_uploaded)==0:
            s=''.join(not_uploaded)
            s='Something went wrong, not all files were uploaded :('
            return s
        _music.refresh() 
        return ''
    finally:
        pass

def _upload_pic_job(server):
    try:
        _gallery.pause()
        _processes.wait() 
        sleep(2)
        chunk_size=128*1024
        total_size=int(server.headers['Content-Length'])
        if (total_size * 5) > _free_disk_space():
            _processes.stop_waiting() 
            return 'Not enough disk splace left'
        form=server.get_post_form()
        p=os.path.join(os.path.dirname(os.path.abspath(__file__)),'photos')
        if not os.path.exists(p):
            os.makedirs(p)
        files = form['picture']
        if files is None or len(files)==0:
            _processes.stop_waiting() 
            return 'Erm, you did not give me a file'

        total_loaded=0
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
                    if not chunk: break
                    pictureout.write(chunk)
            
            if not os.path.isfile(picture_filename):    
                not_uploaded.append(filename)
            else:
                uploaded.append(picture_filename)

        if not len(not_uploaded)==0:
            s=''.join(not_uploaded)
            s='Something went wrong, not all files were uploaded :('
            return s
        _gallery.add_several(uploaded)
        _processes.stop_waiting() 
        return ''
    finally:
        _processes.stop_waiting() 

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
 
    def _upload_music(self):
        res=_waiting_status('Uploading',_upload_music_job,(self,))      
        if res != '':
            _status_update('There was a problem\n%s' % err)
            sleep(10)
        self._send_to('/music?dummy=1')
    
    def _upload_pic(self):
        res=_waiting_status('Uploading',_upload_pic_job,(self,))      
        if res != '':
            _status_update('There was a problem\n%s' % err)
            sleep(10)
        self._send_to('/gallery?dummy=1')
    
    def _upload_video(self):
        res=_waiting_status('Uploading',_upload_video_job,(self,))      
        if res != '':
            _status_update('There was a problem\n%s' % err)
            sleep(10)
        self._send_to('/')
                
    def do_POST(self):
        if 'upload' not in self.path:
            _log.error('Unknonw post request')
            self._send_to('/')
            return
        if 'upload_pic' in self.path:
            self._upload_pic()
        elif 'upload_music' in self.path:
            self._upload_music()
        else:
            self._upload_video()
 
    
    def make_clear_wifi_html(self):
        global _cnt
        _cnt+=1
        form = u"""    
            <p style="font-size:45px">
            This will delete all your wifi settings and reboot, are you sure?
            </p>

            <form action="/reset_wifi_really">
            <input type="hidden" name="hidden_{}" value="{}">
            <button type="submit" name="action" value="really reset {}">
                    Yes, I do know what I'm doing.
            </button></td><td>
            </form>
        """.format(_cnt,_cnt,_cnt)
        return build_html(form)

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
            elif 'music?' in self.path:
                html=_music.make_html()
                self._respond(html)
                return     
            elif 'gallery?' in self.path:
                _processes.play_gallery()
                html=_gallery.make_html()
                self._respond(html)
                return     
            elif 'music_list?' in self.path:
                ps=params['action'][0]
                if 'musicremove' in ps:
                    to_remove=[]
                    for p in params:
                        if 'remove_music_' in p:
                            to_remove.append(params[p][0])
                    
                    if len(to_remove)==0:
                        self._send_to('/music?dummy=1')
                        return
                    indices=','.join(to_remove)
                    html=_music.make_remove_html(indices)
                    self._respond(html)
                    return
                elif 'musicplayall' in ps:
                    to_play=[]
                    for p in params:
                        if 'remove_music_' in p:
                            to_play.append(int(params[p][0]))
                    
                    _processes.play_music(False,to_play)
                    self._send_to('/music?dummy=1')
                    return
                elif 'musicshuffleall' in ps:
                    to_play=[]
                    for p in params:
                        if 'remove_music_' in p:
                            to_play.append(int(params[p][0]))
                    
                    _processes.play_music(True,to_play)
                    self._send_to('/music?dummy=1')
                    return
                elif 'play_music' in ps:
                    index=int(ps[len('play_music '):])
                else: 
                   raise Exception('Unknown request %s' % self.path)
                self._send_to('/music?dummy=1')
                return 
            elif 'really_remove_music?' in self.path:
                _processes.wait()
                _status_update('Removing music, please wait')
                sleep(2)
                ps=params['action'][0]
                indices=[int(i) for i in ps[len('really remove '):].split(',')]
                _music.remove(indices)
                self._send_to('/music?dummy=1')
                _processes.stop_waiting()
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
                    _processes.wait()
                    _status_update('Moving pictures, please wait')
                    sleep(2)
                    _gallery.move_up(ps[len('picup '):])
                    _processes.stop_waiting()
                else: 
                   raise Exception('Unknown request %s' % self.path)
                self._send_to('/gallery?dummy=1')
                return 
            elif 'really_remove_pic?' in self.path:
                _processes.wait()
                _status_update('Removing pictures, please wait')
                sleep(2)
                ps=params['action'][0]
                paths=ps[len('really remove '):].split(',')
                _gallery.remove_several(paths)
                self._send_to('/gallery?dummy=1')
                _processes.stop_waiting()
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
            elif 'add_link?' in self.path:
                if ('name' in params) and ('link' in params):
                    name=params['name'][0]
                    link=params['link'][0]
                    quality=params['quality'][0]
                    if quality=='QUOALITY' or quality=='':
                        quality='default'
                    _processes.kill_running()
                    _streams.add(name,link,quality)
                    _processes.play_stream(name)                    
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
                _status_update('Downloading updates\n'+\
                    'They will take effect when you reboot')
                _update()
                sleep(3)
                _processes.resume()
            elif 'configuration?' in self.path:
                html = _config.get_html()
                self._respond(get_empty_html(html))
                return
            elif 'reset_wifi?' in self.path:        
                html=self.make_clear_wifi_html()
                self._respond(html)
                return
            elif 'reset_wifi_really?' in self.path:
                wifi.clear_wifi()
                _processes.kill_running()
                _processes.wait()
                _status_update('rebooting in a few seconds, see you soon :)')
                Timer(5,_reboot).start()
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
            elif 'scan_wifi?' in self.path:
                html = connection.make_wifi_html() 
                if 'refresh to try again' in html:
                    self._send_to('/scan_wifi_again?dummy=0')
                    return
                self._respond(html)
                return
            elif 'scan_wifi_again?' in self.path:
                _log.info('Scanning again')
                html = connection.make_wifi_html() 
                self._respond(html)
                return
            elif 'reboot?' in self.path:
                _processes.kill_running()
                _processes.wait()
                _status_update('rebooting in a few seconds, see you soon :)')
                Timer(5,_reboot).start()
            elif 'shutdown?' in self.path:
                _processes.kill_running()
                _processes.wait()
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
