from youtube_player import YouTubePlayer
from streamer import Streamer
from file_player import FilePlayer
from cache import Cache
import logger

_cache_size=200
class Player:
    def __init__(self):
        self.yt_player=YouTubePlayer()
        self.streamer=Streamer()
        self.file_player=FilePlayer()
        self.players_cache=Cache(_cache_size)
        self.log=logger.get(__name__)

    def set_status_func(self,status_func):
        self.yt_player.set_status_func(status_func)
        self.streamer.set_status_func(status_func)
        
    def _get_player(self,url):
        c=self.players_cache.get(url)
        if c is not None:
            return c
        
        if self.file_player.can_play(url):
            c=self.file_player
        elif self.yt_player.can_play(url):
            c=self.yt_player
        elif self.streamer.can_play(url):
            c=self.streamer
        
        if c is not None:
            self.players_cache.add(url,c)
            return c
        return None 

    def get_qualities(self,url):
        p=self._get_player(url)
        if p is None: return None
        else: return p.get_qualities(url)

    def can_play(self,url):
        try:
            return self._get_player(url) is not None
        except:
            #TODO: once debugging is done we don't need traces here
            self.log.exception('exception while checkin if can play: ' + url)
            return False

    def is_playing(self):
        return self.yt_player.is_playing() or self.streamer.is_playing() \
             or self.file_player.is_playing()
    
    def play(self,url,quality):
        p=self._get_player(url)
        if p is None: raise Exception('No player found')
        p.play(url,quality)

    def is_playlist(self):
        return self.yt_player.is_playlist()

    def playlist_next(self):
        self.yt_player.playlist_next()

    def stop(self):
        if self.yt_player.is_playing: self.yt_player.stop()
        elif self.streamer.is_playing: self.streamer.stop()
        elif self.file_player.is_playing: self.file_player.stop()
