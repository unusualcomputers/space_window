from youtube_player import YouTubePlayer
from streamer import Streamer
from cache import Cache

_cache_size=200
class Player:
    def __init__(self):
        self.yt_player=YouTubePlayer()
        self.streamer=Streamer()
        self.players_cache=Cache(_cache_size)

    def _get_player(self,url):
        c=self.players_cache.get(url)
        if c is not None:
            print "FOUND PLAYER IN CACHE"
            return c
        
        if self.yt_player.can_play(url):
            c=self.yt_player
        elif self.streamer.can_play(url):
            c=self.streamer
        
        if c is not None:
            self.players_cache.add(url,c)
            print "FOUND PLAYER",c
            return c
        
        raise 'cannot play this video :('

    def get_qualities(self,url):
        return self._get_player(url).get_qualities(url)

    def can_play(self,url):
        try:
            self._get_player(url)
            return True
        except:
            return False

    def is_playing(self):
        return self.yt_player.is_playing() or self.streamer.is_playing()

    def play(self,url,quality):
        self._get_player(url).play(url,quality)

    def stop(self):
        if self.yt_player.is_playing: self.yt_player.stop()
        elif self.streamer.is_playing: self.streamer.stop()
