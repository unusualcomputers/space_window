import pafy
import os
import threading
import thread
import time
from cache import Cache
from player_base import VideoPlayer
import logger


_cache_size=100
_default_res=360
_thread_id=0

def _next_thred_id():
    global thread_id
    thread_id+=1
    return thread_id

class YouTubePlayer(VideoPlayer):
    def __init__(self,
            status_func=None,
            player=None,
            player_args=None):
        VideoPlayer.__init__(self,status_func,player,player_args)
        self.video_cache=Cache(_cache_size)
        self.playlist_cache=Cache(_cache_size)
        self.lock=threading.Lock()
        self.alive_threads=[]
        self.playing_playlist=False

    def can_play(self,url):
        self._status('checking video status')
        return (pafy.playlist.extract_playlist_id(url) is not None) or \
            (self._get_video(url) is not None)         

    def _get_video(self,url):
        v=self.video_cache.get(url)
        if v is not None:
            return v
        try:
            v=pafy.new(url)
            if v.length == 0.0: return None #live stream
            self.video_cache.add(url,v)
            return v
        except:
            return None

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

    def _get_video_qualities(self,pfy):
        mp4s=filter(lambda s: s.extension=='mp4',pfy.streams)
        resolutions=[mp4.quality for mp4 in mp4s]
        ret=[]
        for r in resolutions:
            i=r.find('x')
            if i==-1: ret.append(r) 
            else: ret.append(r[i+1:]+'p')
        ret=ret+['worst','default','best']
        return ret

    def _get_playlist_qualities(self,pfys):
        # get all qualities for all lists
        # then return a list of those that appear everywhere
        sz=len(pfys)
        i=1
        qualities=[]
        for pfy in pfys:
            self._status('getting video quality data for video %i of %i' \
                %(i,sz))
            i=i+1
            qualities.append(self._get_video_qualities(pfy))
        first=qualities[0]
        rest=qualities[1:]
        ret=[]
        for f in first:
            t=[q for q in rest if f in q]
            if len(t)==len(rest): ret.append(f)
        return ret

    def _get_video_url(self,pfy,quality):
        # quality is a string with the second part of resolution and 'p'
        # e.g. 1280x720 -> 720p
        # or 'best' 
        # or just some string
        # return a list, just easier like that
        try:
            if pfy is None: return []
            title=pfy.title
            author=pfy.author
            mp4s=filter(lambda s: s.extension=='mp4',pfy.streams)
            if len(mp4s)==0:return []
            if quality=='worst' or len(mp4s)==1:
                return [mp4s[0].url]
            if quality=='best':
                return [pfy.getbestvideo('mp4').url]
            if quality[-1]=='p': 
                s='x'+quality[:-1]
                try:
                    nq=int(quality[:-1])
                except:
                    nq=_default_res
            else: 
                s=quality
                nq=_default_res

            if quality != 'default':
                for ss in mp4s:
                    if s in ss.quality:
                        return [(title,author,ss.url)]
            
            # not found, look for first smaller than nq
            smaller=[]
            for ss in mp4s:
                try:
                    q=int(ss.quality.split('x')[-1])
                except:
                    break
                if q<nq: smaller.append(ss)
            if len(smaller)>0:
                return [(title,author,smaller[-1].url)]    
            # if nothing else worked, get me the best one
            return [(title,author,pfy.getbestvideo('mp4').url)]
        except:
            return []

    def _get_first_url(self,url,quality,urls):
        pl=self._get_playlist(url)
        sz=1
        if pl is None:
            pfy=self._get_video(url)
            urls+=self._get_video_url(pfy,quality)
        else:
            sz=len(pl['items'])
            if sz==0: return sz
            self._status('getting data for video 1 of %i'%sz)
            urls+=self._get_video_url(pl['items'][0]['pafy'],quality)
        return sz

    def _get_remaining_urls(self,url,quality,urls,thread_id):
        try:        
            with self.lock:
                self.alive_threads.append(thread_id)
            pl=self._get_playlist(url)
            if pl is None: 
                return
            rest=pl['items'][1:]
            sz=len(rest)+1
            j=2
            for i in rest:
                self._status('getting data for video %i of %i'%(j,sz))
                j+=1
                u=self._get_video_url(i['pafy'],quality)
                with self.lock:
                    urls+=u
                    if thread_id not in self.alive_threads: return
        except:
            log=logger.get(__name__)
            log.exception('exception while getting remaining you tube urls')
            raise
    
    def _play_loop_impl(self,url,quality):
        try:
            with self.lock:
                thread_id=_next_thread_id()
                self.alive_threads.append(thread_id)
            
            self._status('retrieving videos...')
            urls=[]
            s = self._get_first_url(url,quality,urls)
            self.playing_playlist=(s > 1)
            threading.Thread(target=self._get_remaining_urls,
                args=(url,quality,urls,_next_thread_id)).start()
            prev_sz=1
            while True:
                with self.lock:
                    sz=len(urls)
                        
                if sz > prev_sz:
                    first=prev_sz
                    prev_sz=sz
                else:
                    first=0
                for i in range(first,sz):
                    if not self.playing: return
                    with self.lock:
                        (name,author,u)=urls[i]
                        if thread_id not in self.alive_threads: return
                    self._status('playing\n%s\n%s' % (name,author))
                    print 'playing\n%s\n%s' % (name,author)
                    cmd='%s "%s"' % (self._player_cmd,u)
                    os.system(cmd)
        finally:
            self.playing_playlist=False

    def _stop_threads(self):
        with self.lock:
            self.alive_threds=[]

    def is_playlist(self):
        return self.playing_playlist

    def playlist_next(self):
        with self.lock:
            if self.playing_playlist: self._kill_player()

    def get_qualities(self,url):
        self._status('getting playlist information for ' + url)
        v=self._get_playlist(url)
        if v is not None: 
            v=[vv['pafy'] for vv in v['items']] 
            self._status('getting available video qualities for the playlist')
            return self._get_playlist_qualities(v)
        #self._status('this was not a playlist, getting video information')
        v=self._get_video(url)
        if v is not None: 
            self._status('getting available video qualities')
            return self._get_video_qualities(v)
        return None

