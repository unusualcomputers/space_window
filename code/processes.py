from __future__ import unicode_literals
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
from gallery import Gallery
from music import Music
from config_util import Config
_standalone=False
_log=logger.get(__name__)

def set_standalone(standalone):
    global _standalone
    _standalone=standalone
    streamsmod.set_standalone(standalone)

class ProcessHandling:
    def __init__(self,status_update_func):
        config = Config('space_window.conf',__file__)    
        self._start_with=config.get('global','start_with','streams')
        self._current_stream=None
        self._resume_stream=None
        self._check_timer_delay=20
        self._check_timer=None
        self._wait=False
        self._streams=Streams.load()
        self._nasa=NasaPod()
        self._gallery=Gallery(status_update_func)
        self._music=Music(status_update_func)
        self._clock=Clock()
        self._mopidy=None
        self._status_update=status_update_func    
        if not _standalone:
            threading.Thread(target=self.launch_mopidy).start()
        self._streams.set_status_func(status_update_func)
        self._resume_func=self.run_something

    def pause(self):
        self._stop_timer()
        self.wait()
        if self._streams.is_playing():
            self._resume_stream=self._current_stream
            self._resume_func=self._play_current_stream
        elif self._nasa.is_playing():
            self._resume_func=self.play_nasa
        elif self._clock.is_playing():
            self._resume_func=self.play_clock
        elif self._gallery.is_playing():
            self._resume_func=self.play_gallery
        self.kill_running()
        
    def resume(self):
        self.stop_waiting()
        _log.info('resume func is %s' % self._resume_func)
        self._current_stream=self._resume_stream
        self._resume_stream=None
        self._resume_func()
        self._resume_func=self.run_something

    def reload_config(self):
        self.pause()
        sleep(5)
        self._nasa.load_config()
        self._gallery.load_config()
        self._music.load_config()
        self._clock.load_config()
        self.resume()

    def launch_mopidy(self):
        try:
            if _standalone: return
            self._mopidy=MopidyUpdates(self._status_update)
            self._mopidy.show_updates()
        except:
            _log.exception('exception while launching mopidy')
            
    def streams(self):
        return self._streams
            
    def kill_running(self):
        _log.info('stopping running shows')
        self._stop_timer()
        self._streams.stop()
        self._nasa.stop()
        self._gallery.stop()
        self._music.stop()
        self._clock.stop()
        if not _standalone and self._mopidy is not None:
            self._mopidy.stop()
        self._current_stream=None
       
    def wait(self):
        self._wait=True

    def stop_waiting(self):
        self._wait=False

    def _stop_timer(self):
        if self._check_timer is not None: self._check_timer.cancel()

    def _start_timer(self):
        self._check_timer=Timer(self._check_timer_delay, self.run_something)
        self._check_timer.start()
 
    def _play_current_stream(self):
        if self._current_stream is None:
            self.play_next()
        else:
            self.play_stream(self._current_stream)

    def play_stream(self,name):
        self._stop_timer()
        _log.info('starting %s' % name)
        if self._current_stream==name and self._streams.is_playing():
            _log.info('stream %s is already playing' % name)
            return
        self.kill_running()   
        self._status_update('starting %s' % name)
        self._current_stream=name
        self._streams.play(name)
        #self._status_update('playing %s' % name)
        #sleep(3)
        self._start_timer()

    def play_music(self,shuffle,i):
        _log.info('stopping running shows')
        self._stop_timer()
        self._streams.stop()
        if not _standalone and self._mopidy is not None:
            self._mopidy.stop()
        self._current_stream=None
        self._music.stop()
        self._music.play(shuffle,i)
        self._start_timer()
    
    def play_gallery(self):
        if self._gallery.is_playing(): return
        _log.info('stopping running shows')
        self._stop_timer()
        self._streams.stop()
        self._nasa.stop()
        self._gallery.stop()
        self._clock.stop()
        self._current_stream=None
        self._gallery.play()
        self._start_timer()
    
    def play_nasa(self):
        if self._nasa.is_playing(): return
        self._stop_timer()
        self._streams.stop()
        self._gallery.stop()
        self._clock.stop()
        self._current_stream=None
        self._nasa.play()
        self._start_timer()
    
    def play_clock(self):
        if self._clock.is_playing(): return
        self._stop_timer()
        self._streams.stop()
        self._nasa.stop()
        self._gallery.stop()
        self._clock.stop()
        self._current_stream=None
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
            _log.info('about to play apod')
            self.play_nasa()
        else: 
            self._current_stream=name
            _log.info('about to play stream %s' % name)
            self.play_stream(name)

    def _something_playing(self):
        return (self._streams.is_playing() or self._nasa.is_playing()\
            or self._clock.is_playing() or self._gallery.is_playing() or \
            self._music.is_playing() or self._wait)

    def run_first_time(self):
        if _standalone:
            self.run_something()
            return
        self._stop_timer()
        if self._something_playing():
            self._start_timer()
            return

        if self._start_with=='clock':
            self.play_clock()
        elif self._start_with=='nasa':
            self.play_nasa()
        elif self._start_with=='gallery':
            self.play_gallery()
        else:
            self.play_next()
        self._start_timer()

    def run_something(self):
        self._stop_timer()
        if self._something_playing():
            self._start_timer()
            return

        if _standalone:
            if self._start_with=='gallery':
                self.play_gallery()
            else:    
                name=self._streams.first()
                if name is not None:
                    _log.info('about to play %s' % name)
                    self.play_stream(name)
                else:
                    self.play_gallery()
            self._start_timer()
            return

        self.play_next()
        self._start_timer()
        
    def refresh_caches(self):
        self.pause()
        self._streams.refresh_caches()
        self.resume()

    def gallery(self):
        return self._gallery
    
    def music(self):
        return self._music
