import pafy
import os
import threading
import time
from cache import Cache
from datetime import datetime

_player_cmd='omxplayer'
_player_args='--vol 500 --timeout 60'
#_player_cmd='mplayer'
#_player_args='-cache 8192'

_cache_size=200

def _now():
    return datetime.now()

class YouTubePlayer:
    def __init__(self):
        self.run=False
        self.video_cache=Cache(_cache_size)
        self.playlist_cache=Cache(_cache_size)
        self._status_func=None
        self.lock=threading.Lock()

    def set_status_func(self,func):
         self._status_func=func

    def _status(self,msg):
        if self._status_func is not None:
            self._status_func(msg)
        else:
            print msg

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
                    nq=360
            else: 
                s=quality
                nq=360

            if quality != 'default':
                for ss in mp4s:
                    if s in ss.quality:
                        return [ss.url]
            
            # not found, look for first smaller than nq
            smaller=[]
            for ss in mp4s:
                try:
                    q=int(ss.quality.split('x')[-1])
                except:
                    break
                if q<nq: smaller.append(ss)
            if len(smaller)>0:
                return [smaller[-1].url]    
            # if nothing else worked, get me the best one
            return [pfy.getbestvideo('mp4').url]
        except:
            return []


    def _get_playlist_urls(self,url,quality):
        pl=self._get_playlist(url)
        if pl is None:
            return []
        sz=len(pl['items'])
        ret=[]
        i=1
        for v in pl['items']:
            self._status('getting data for video %i of %i'%(i,sz))
            i=i+1
            ret=ret+self._get_video_url(v['pafy'],quality)
        return ret        

    def _get_urls(self,url,quality):
        urls=self._get_playlist_urls(url,quality)
        if len(urls)==0:
            pfy=self._get_video(url)
            urls=self._get_video_url(pfy,quality)
        return urls

    def _get_first_url(self,url,quality,urls):
        pl=self._get_playlist(url)
        if pl is None:
            pfy=self._get_video(url)
            urls+=self._get_video_url(pfy,quality)
        else:
            sz=len(pl['items'])
            if sz==0: return
            self._status('getting data for video 1 of %i'%sz)
            urls+=self._get_video_url(pl['items'][0]['pafy'],quality)
    
    def _get_remaining_urls(self,url,quality,urls):
        pl=self._get_playlist(url)
        if pl is None: return
        rest=pl['items'][1:]
        sz=len(rest)+1
        j=2
        for i in rest:
            self._status('getting data for video %i of %i'%(j,sz))
            j+=1
            u=self._get_video_url(i['pafy'],quality)
            self.lock.acquire()
            urls+=u
            self.lock.release()

    def _play_loop(self,url,quality):
        self._status('Retrieving videos...')
        urls=[]
        self._get_first_url(url,quality,urls)
 
        threading.Thread(target=self._get_remaining_urls,
            args=(url,quality,urls)).start()
        prev_sz=1
        while True:
            self.lock.acquire()
            sz=len(urls)
            if sz > prev_sz:
                first=prev_sz
                prev_sz=sz
            else:
                first=0
            self.lock.release()
            for i in range(first,sz):
                if not self.run: return
                self.lock.acquire()
                u=urls[i]
                self.lock.release()
                cmd='%s %s "%s"' % (_player_cmd,_player_args,u)
                os.system(cmd)

    #def _play_loop(self,url,quality):
    #    self._status('Retrieving videos...')
    #    urls=self._get_urls(url,quality)
    #    while True:
    #        for url in urls:
    #            if not self.run: return
    #            cmd='%s %s "%s"' % (_player_cmd,_player_args,url)
    #            os.system(cmd)

    def get_qualities(self,url):
        self._status('getting playlist information')
        v=self._get_playlist(url)
        if v is not None: 
            v=[vv['pafy'] for vv in v['items']] 
            self._status('getting available video qualities for the playlist')
            return self._get_playlist_qualities(v)
        self._status('oups, this was not a playlist, getting video information')
        v=self._get_video(url)
        if v is not None: 
            self._status('getting available video qualities')
            return self._get_video_qualities(v)
        self._status('this is not a youtube video')
        return []

    def can_play(self,url):
        self._status('checking video status for ' + url)
        return ((self._get_video(url) is not None) or\
            (self._get_playlist(url) is not None))

    def play(self,url,quality):
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


