import pafy
import os
import threading
import thread
import time
from cache import Cache
from player_base import VideoPlayer
import logger
import json

_cache_size=100
_default_res=360
_thread_id=0
_log=logger.get(__name__)

def _next_thread_id():
    global _thread_id
    _thread_id+=1
    return _thread_id

class YouTubePlayer(VideoPlayer):
    def __init__(self,
            status_func=None):
        VideoPlayer.__init__(self,status_func)
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
            _log.exception('exception while getting video for '+url)
            return None

    def _get_playlist(self,url):
        v=self.playlist_cache.get(url)
        if v is not None: 
            return v
        try:
            plid=pafy.playlist.extract_playlist_id(url)
            if not plid:
                return None
            gurl=pafy.g.urls['playlist'] % plid
            allinfo=pafy.pafy.fetch_decode(gurl)
            allinfo=json.loads(allinfo)
            pafys=[]
            for v in allinfo['video']:
                plentry=[v.get('encrypted_id'),None]
                pafys.append(plentry)
            self.playlist_cache.add(url,pafys)
            return pafys
        except:
            _log.exception('exception while playlist for '+url)
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
            #self._status('getting video quality data for video %i of %i' \
            #    %(i,sz))
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
                return [pfy.getbest('mp4').url]
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
            return [(title,author,pfy.getbest('mp4').url)]
        except:
            _log.exception('exception while getting video url')
            return []

    def _get_first_url(self,url,quality,urls):
        pl=self._get_playlist(url)
        sz=1
        if pl is None:
            _log.info('getting first url')
            pfy=self._get_video(url)
            urls+=self._get_video_url(pfy,quality)
        else:
            _log.info('getting first url for playlist')
            pfy=self._get_video(url)
            sz=len(pl)
            if sz==0: return sz
            #self._status('getting data for your video')
            pfy=pl[0][1]
            if pfy is None:
                pfy=pafy.new(pl[0][0])
                pl[0][1]=pfy
            urls+=self._get_video_url(pfy,quality)
        return sz

    def _get_remaining_urls(self,url,quality,urls,thread_id):
        try:        
            pl=self._get_playlist(url)
            if pl is None: 
                return
            rest=pl[1:]
            sz=len(rest)+1
            j=2
            new_pfys=[pl[0]]
            for i in rest:
                #self._status('getting data for video %i of %i'%(j,sz))
                _log.info('getting data for video %i of %i'%(j,sz))
                j+=1
                pfy=i[1]
                if pfy is None:
                    pfy=pafy.new(i[0])
                    i[1]=pfy
                u=self._get_video_url(pfy,quality)
                with self.lock:
                    urls+=u
                    if thread_id not in self.alive_threads: return
        except:
            _log.exception('exception while getting remaining you tube urls')
            raise
    
    def _play_loop_impl(self,url,quality):
        thread_id=_next_thread_id()
        try:
            with self.lock:
                self.alive_threads=[]
                self.alive_threads.append(thread_id)
            
            self._status('retrieving videos...')
            urls=[]
            s = self._get_first_url(url,quality,urls)
            self.playing_playlist=(s > 1)
            if self.playing_playlist:
                threading.Thread(target=self._get_remaining_urls,
                    args=(url,quality,urls,thread_id)).start()
            prev_sz=1
            first=0
            with self.lock:
                sz=len(urls)
                        
            while True:
                for i in range(first,sz):
                    if not self.playing: return
                    with self.lock:
                        (name,author,u)=urls[i]
                        if thread_id not in self.alive_threads: return
                    self._status('playing\n%s\n%s' % (name,author))
                    if s==1:
                        cmd='%s "%s"' % (self._player_cmd,u)
                    else:
                        cmd='%s "%s"' % (self._player_pl_cmd,u)
                    #_log.info(cmd)
                    os.system(cmd)
                    #_log.info('Done playing: ' + cmd)
                    self._status('')
 
                with self.lock:
                    sz=len(urls)
                        
                if sz > prev_sz:
                    first=prev_sz
                    prev_sz=sz
                else:
                    first=0
        except:
            _log.exception('exception while playing '+url)
        finally:
            with self.lock:
                if thread_id in self.alive_threads:
                    self.alive_threads.remove(thread_id)
            self.playing_playlist=False

    def _stop_threads(self):
        with self.lock:
            self.alive_threads=[]

    def is_playlist(self):
        return self.playing_playlist

    def playlist_next(self):
        with self.lock:
            if self.playing_playlist: self._kill_player()

    def get_qualities(self,url):
        self._status('getting playlist information for ' + url)
        v=self._get_playlist(url)
        if v is not None: 
            self._status('getting available video qualities for the playlist')
            return ['default']#self._get_playlist_qualities(v)
        #self._status('this was not a playlist, getting video information')
        _log.info('getting qualities')
        v=self._get_video(url)
        if v is not None: 
            self._status('getting available video qualities')
            return self._get_video_qualities(v)
        return None

