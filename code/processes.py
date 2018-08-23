import threading
from nasa_pod import NasaPod
from clock import Clock
from threading import Timer
import wifi_control as wifi
from mopidy_listener import MopidyUpdates
from streams import Streams
import streams as streamsmod
import logger
from time import sleep

_standalone=False

def set_standalone(standalone):
    global _standalone
    _standalone=standalone
    streamsmod.set_standalone(standalone)

class ProcessHandling:
    def __init__(self,status_update_func):
        self._current_stream=None
        self._check_timer_delay=30
        self._check_timer=None
        self._wait=False
        self._streams=Streams.load()
        self._nasa=NasaPod()
        self._clock=Clock()
        self._mopidy=None
        if not _standalone:
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
        if _standalone: return
        if self._mopidy is None:
            self._mopidy=MopidyUpdates(self._status_update)
        self._mopidy.show_updates()
            
    def streams(self):
        return self._streams
            
    def kill_running(self,reset_current=False):
        self.log.info('stopping running shows')
        #if(updates):
        #    self._status_update('stopping running shows')
        if self._check_timer is not None: 
            self._check_timer.cancel()
        self._streams.stop()
        self._nasa.stop()
        self._clock.stop()
        if not _standalone and self._mopidy is not None:
            self._mopidy.stop()
        if reset_current:
            self._current_stream=None
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
            self.log.info('stream %s is already playing' % name)
            return
        self.kill_running()   
        self._status_update('starting %s' % name)
        self._current_stream=name
        self._streams.play(name)
        self._status_update('playing %s\ngive me a few seconds' % name)
        sleep(3)
        self._status_update(name)
        self._start_timer()

    def play_apod(self):
        self._stop_timer()
        self.log.info('stopping streams')
        self._current_stream=None
        self.log.info('playing apod')
        self._streams.stop()
        self._clock.stop()
        self._nasa.play()
        self._start_timer()
     
    def play_clock(self):
        self._stop_timer()
        self.log.info('stopping streams')
        self._current_stream=None
        self.log.info('playing apod')
        self._streams.stop()
        self._nasa.stop()
        self._clock.play()
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
        self._stop_timer()
        if (self._streams.is_playing() or self._nasa.is_playing()\
            or self._clock.is_playing() or self._wait):
            self._start_timer()
            return

        if _standalone:
            name=self._streams.first()
            if name is not None:
                self.log.info('about to play %s' % name)
                self.play_stream(name)
            self._start_timer()
            return

        self.play_next()
        self._start_timer()
        
    def refresh_caches(self):
        self._streams.refresh_caches(True)
