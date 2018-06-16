import pafy
import os
import threading
import time
from cache import Cache
from datetime import datetime

#_player_cmd='omxplayer'
#_player_args='--vol 500 --timeout 60'
_player_cmd='mplayer'
_player_args='-cache 8192'

_cache_size=200

def _now():
    return datetime.now()

class YouTubePlayer:
    def __init__(self):
        self.run=False
        self.video_cache=Cache(_cache_size)
        self.playlist_cache=Cache(_cache_size)
        
    def _get_video(self,url):
        v=self.video_cache.get(url)
        if v is not None:
            return v
        try:
            v=pafy.new(url)
            self.video_cache.add(url,v)
            return v
        except:
            None

    def _get_playlist(self,url):
        v=self.playlist_cache.get(url)
        if v is not None: 
            return v
        try:
            v=pafy.get_playlist(url)
            self.playlist_cache.add(url,v)
            return v
        except:
            return None

    def _get_video_url(self,pfy,quality):
        # quality is a string with the second part of resolution and 'p'
        # e.g. 1280x720 -> 720p
        # or 'best' 
        # or just some string
        # return a list, just easier like that
        try:
            if pfy is None: return []
            if quality=='best':
                return [pfy.getbestvideo('mp4').url]
            if quality[-1]=='p': s='x'+quality[:-1]
            else: s=quality
            
            for ss in pfy.streams:
                if ss.extension=='mp4' and s in ss.quality:
                    return [ss.url]
            # if nothing else worked, get me the best one
            return [pfy.getbestvideo('mp4').url]
        except:
            return []


    def _get_playlist_urls(self,url,quality):
        pl=self._get_playlist(url)
        if pl is None:
            return []
        ret=[]
        for v in pl['items']:
            ret=ret+self._get_video_url(v['pafy'],quality)
        return ret        

    def _get_urls(self,url,quality):
        urls=self._get_playlist_urls(url,quality)
        if len(urls)==0:
            pfy=self._get_video(url)
            urls=self._get_video_url(pfy,quality)
        return urls

    def _get_video_qualities(self,pfy):
        mp4s=filter(lambda s: s.extension=='mp4',pfy.streams)
        resolutions=[mp4.quality for mp4 in mp4s]
        print resolutions
        ret=[]
        for r in resolutions:
            i=r.find('x')
            if i==-1: ret.append(r) 
            else: ret.append(r[i+1:]+'p')
        ret.append('best')
        return ret

    def _get_playlist_qualities(self,pfys):
        # get all qualities for all lists
        # then return a list of those that appear everywhere
        qualities=[self._get_video_qualities(pfy) for pfy in pfys]
        first=qualities[0]
        rest=qualities[1:]
        print "ALL:", qualities,first
        ret=[]
        for f in first:
            t=[q for q in rest if f in q]
            if len(t)==len(rest): ret.append(f)
        print "filtered",ret
        return ret

    def _play_loop(self,url,quality):
        urls=self._get_urls(url,quality)
        print "urls:",urls
        while True:
            for url in urls:
                if not self.run: return
                print "starting ",url
                cmd='%s %s "%s"' % (_player_cmd,_player_args,url)
                os.system(cmd)

    def get_qualities(self,url):
        v=self._get_playlist(url)
        if v is not None: 
            v=[vv['pafy'] for vv in v['items']] 
            return self._get_playlist_qualities(v)
        v=self._get_video(url)
        if v is not None: 
            return self._get_video_qualities(v)
        return []

    def can_play(self,url):
        return ((self._get_video(url) is not None) or\
            (self._get_playlist(url) is not None))

    def play(self,url,quality):
        qualities=self.get_qualities(url)
        if quality not in qualities: return False
        if self.run: self.stop()
        else: os.system('pkill -9 %s' % _player_cmd)
        self.run=True
        threading.Thread(target=self._play_loop,args=(url,quality)).start()
        return True

    def stop(self):
        if not self.run: return
        self.run=False    
        os.system('pkill -9 %s' % _player_cmd)
        time.sleep(0.1)#poor man's sychronisation
        os.system('pkill -9 %s' % _player_cmd)


