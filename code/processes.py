import threading
from nasa_pod import NasaPod
from threading import Timer
import wifi_setup_ap.wifi_control as wifi
from mopidy_listener import MopidyUpdates
from streams import Streams
import logger

class ProcessHandling:
    def __init__(self,status_update_func):
        self._current_stream=None
        self._check_timer_delay=20
        self._check_timer=None
        self._wait=False
        self._streams=Streams.load()
        self._nasa=NasaPod()
        threading.Thread(target=self.launch_mopidy).start()
        self._status_update=status_update_func    
        self._streams.set_status_func(status_update_func)
        self.log=logger.get(__name__)

    def launch_mopidy(self):
        try:
            self._mopidy=MopidyUpdates(self._status_update)
        except:
            self.log.exception('exception while launching mopidy')
            
    def start_mopidy(self):
        if self._mopidy is None:
            self._mopidy=MopidyUpdates(self._status_update)
        self._mopidy.show_updates()
            
    def streams(self):
        return self._streams
            
    def kill_running(self,updates=True):
        self.log.info('stopping running shows')
        #if(updates):
        #    self._status_update('stopping running shows')
        if self._check_timer is not None: 
            self._check_timer.cancel()
        self._streams.stop()
        self._nasa.stop()
        self._mopidy.stop()
        #wifi.run('pkill -9 mopidy')
       
    def wait(self):
        self._wait=True

    def stop_waiting(self):
        self._wait=False

    def _stop_timer(self):
        if self._check_timer is not None: self._check_timer.cancel()

    def _start_timer(self):
        self._check_timer=Timer(self._check_timer_delay, self.run_something)
        self._check_timer.start()
 
    def play_stream(self,name):
        self._stop_timer()
        self.log.info('starting %s' % name)
        if self._current_stream==name and self._streams.is_playing():
            self.log.info('stream %s is aready playing')
            return
        self.kill_running()   
        self._status_update('starting %s' % name)
        self._current_stream=name
        self._streams.play(name)
        self._status_update('playing %s\ngive me a few seconds' % name)
        self._start_timer()

    def play_apod(self):
        self._stop_timer()
        self.log.info('stopping streams')
        self._current_stream=None
        self.log.info('playing apod')
        self._streams.stop()
        self._nasa.play()
        self._start_timer()
     
    def play_next(self):
        if self._streams.is_playlist():
            self._streams.playlist_next()
            return
        if self._current_stream is None:
            name=self._streams.first()
        else:
            name=self._streams.next(self._current_stream) 
        if name is None: 
            self.log.info('about to play apod')
            self.play_apod()
        else: 
            self.log.info('about to play stream %s' % name)
            self.play_stream(name)

    def run_something(self):
        if self._wait: return
        self._stop_timer()
        if not (self._streams.is_playing() or self._nasa.is_playing()):
            self.play_next()
        self._start_timer()
        
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
