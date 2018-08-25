import os
import time
import threading
import logger
from config_util import Config

_player='omxplayer'
_player_args='-o alsa--vol 500 --timeout 60'
#_player='mpv'
#_player_args=''
_synchronisation_sleep=0.1

class PlayerBase:
    def __init__(self,
            status_func=None):
        self._status_func=status_func
        self.playing=False
        config = Config('space_window.conf',__file__)    
        self._player=config.get('player','player',_player)
       
        self._player_args=config.get('player','player_args',_player_args)
        self._player_pl_args=config.get('player','playlist_player_args',\
                _player_args)
        
        self._player_cmd=self._player+' '+self._player_args
        self._player_pl_cmd=self._player+' '+self._player_pl_args
        self.log=logger.get(__name__)

    def set_status_func(self,func):
         self._status_func=func

    def _status(self,msg):
        if self._status_func is not None:
            self._status_func(msg)
        else:
            self.log.info(msg)

    def _play_loop_impl(self,url,quality):
        raise Exception('play loop is not implemented')
    
    def _play_loop(self,url,quality):
        try:
            self.log.debug('STARTING PLAYER LOOP')
            self._play_loop_impl(url,quality)
        except:
            self.log.exception('player loop exception')
        finally:
            self.playing=False

    def get_qualities(self,url):
        raise Exception('get_qualities not implemented')

    def can_play(self,url):
        self._status('checking video status')
        try:
            return self.get_qualities(url) is not None
        except:
            return False

    def is_playing(self):
        return self.playing

    def _kill_player(self):
        os.system('pkill -9 %s' % self._player)

    def play(self,url,quality):
        self.stop()
        self.playing=True
        threading.Thread(target=self._play_loop,args=(url,quality)).start()
        time.sleep(_synchronisation_sleep)#poor man's sychronisation

    def _stop_threads(self):
        pass

    def stop(self):
        self._stop_threads()
        self.playing=False    
        self._kill_player()
        time.sleep(_synchronisation_sleep)#poor man's sychronisation
        self._kill_player()


