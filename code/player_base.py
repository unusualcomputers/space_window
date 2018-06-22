import os
import time
import threading

#_player='omxplayer'
#_player_args='--vol 500 --timeout 60'
_player='mpv'
_player_args=''
_synchronisation_sleep=0.1

class VideoPlayer:
    def __init__(self,
            status_func=None,
            player=None,
            player_args=None):
        self._status_func=status_func
        self.playing=False
        if player is None:
            self._player=_player
        else:
            self._player=player
       
        if player_args is None:
            self._player_args=_player_args
        else: 
            self._player_args=player_args
        
        self._player_cmd=self._player+' '+self._player_args

    def set_status_func(self,func):
         self._status_func=func

    def _status(self,msg):
        if self._status_func is not None:
            self._status_func(msg)
        else:
            print msg

    def _play_loop_impl(self,url,quality):
        raise 'play loop is not implemented, create one of my children'
    
    def _play_loop(self,url,quality):
        try:
            self._play_loop_impl(url,quality)
        except:
            pass
        finally:
            self.playing=False

    def get_qualities(self,url):
        raise 'get_qualities not implemented, create one of my children'

    def can_play(self,url):
        self._status('checking video status')
        try:
            self.get_qualities(url)
            return True
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


