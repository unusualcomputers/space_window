from jsonable import Jsonable
import os
from html import build_html
from collections import OrderedDict
from video_player import Player
import threading
import logger
import random
import requests

_streams_data='.space.window'
_base_path=os.path.join(os.path.expanduser('~'),_streams_data)
_config_path=os.path.join(_base_path,_streams_data)
_cnt=random.randint(0,1000) # global counter, used to make html more responsive
_session=requests.Session()
_player=None
# streams
#   main class managing sreams to play

_standalone=False

def set_standalone(standalone):
    global _standalone
    _standalone=standalone

class Streams(Jsonable):

    @classmethod
    def load(cls):
        if not cls.file_exists(_base_path):
            os.mkdir(_base_path)
        path=_config_path
        if cls.file_exists(path):
            s=cls.from_file(path)
            s._initialise()
        else:
            s=cls()
            s.save()
        return s                

    def save(self):
        self.to_file(_config_path)
     
    def _initialise(self):
        self.log=logger.get(__name__)
        self.refresh_caches(True)
    
    def __init__(self,streams=OrderedDict()):
        self.streams=streams
        self._initialise()

    def _get_data_for_first_video(self):
        if self.len() == 0: return
        (url,quality)=self.streams.items()[0][1]
        try:
            self.log.info('getting data for first video: '+url)
            _player.can_play(url)
            self.log.info('got data for first video: ' + url)
        finally:
            pass

    def set_status_func(self,status_func):
        global _player
        if _player is not None:
            _player.set_status_func(status_func)

    def refresh_caches(self):
        global _player
        _player=Player()
        if not _standalone:
            self._get_data_for_first_video()
    
    def len(self):
        return len(self.streams.items())

    def first(self):
        if not _standalone:
            return self.at(0)
        else:
            for name in self.streams:
                (url,quality)=self.streams[name]
                if os.path.isfile(url): return name

    def at(self,i):
        if i >= self.len():
            return None
        else:
            return self.streams.items()[i][0]
  	
    def next(self, name):
        found=False
        for k in range(self.len()):
           if self.at(k)==name:
                if not _standalone: return self.at(k+1)
                else: found = True
           elif found:
                if os.path.isfile(at(k)): return at(k)
        return self.first()

    def is_playlist(self):
        return _player.is_playlist()

    def add(self, name, url, quality):
        if not os.path.isfile(url):
            resp=_session.head(url,allow_redirects=True)
            url=resp.url
        if not _player.can_play(url):
            raise Exception('Cannot play ' + url)
        self.streams[name]=(url,quality)
        #threading.Thread(target=_player.can_play,args=(url))
        self.save()
        
    def remove(self,name):
        i=self.find(name)
        if i!=-1:
            (url,q)=self.streams[name]
            if os.path.isfile(url):
                srt=os.path.splitext(url)[0]+'.srt'
                os.remove(url)
                if os.path.isfile(srt):
                    os.remove(srt)
            self.streams.pop(name,None)
            self.save()
    
    def find(self,name):
        for i in range(0,self.len()):
            if self.at(i) == name: return i
        return -1

    def up(self,name):
        i=self.find(name)
        if i==-1: return
        if i<=0 or i>=self.len():
            return
        l=self.streams.keys()
        c=l[i]
        l[i]=l[i-1]
        l[i-1]=c
        d=OrderedDict()
        for i in l:
            d[i]=self.streams[i]
        self.streams=d
        self.save()

    def make_remove_html(self,name):
        form = u"""    
            <p style="font-size:45px">Really, really remove {}?</p>

            <form action="/really_remove">
            <input type="hidden" name="hidden_{}" value="{}">
            <button type="submit" name="action" value="really remove {}">
                    Yes, really remove it!
            </button></td><td>
            </form>
        """.format(name,name,name,name)
        return build_html(form)

    def make_html(self):
        global _cnt
        _cnt+=1
        html=u''
        for name in self.streams:
            (url,quality)=self.streams[name]
            if _standalone and not os.path.isfile(url): continue
            if os.path.isfile(url):
                row = u"""<tr><td>{}</td><td>{}</td><td>
                    <input type="hidden" name="hidden_{}" value="{}">
                    <button type="submit" name="action" value="play {}">
                        Play
                    </button></td><td>
                    <button type="submit" name="action" value="moveup {}">
                        Up</button></td>
                    <td>
                    <button type="submit" name="action" value="remove {}">
                            Remove
                    </button></td>
                    </tr>
                    """.format(name,quality,_cnt,name,name,name,name)
            else:
                row = u"""<tr><td>{}</td><td>{}</td><td>
                    <input type="hidden" name="hidden_{}" value="{}">
                    <button type="submit" name="action" value="play {}">
                        Play
                    </button></td><td>
                    <button type="submit" name="action" value="moveup {}">
                        Up</button></td>
                    <td>
                    <button type="submit" name="action" value="remove {}">
                        Remove
                    </button></td>
                    <td><a href="{}" target="_blank"> Show in browser </a></td>
                    </tr>
                    """.format(name,quality,_cnt,name,name,name,name,url)
            html+=row
        return html
        
    def play(self,name):
        (url,quality)=self.streams[name]
        _player.play(url,quality)

    def playlist_next(self):
        _player.playlist_next()

    def stop(self):
        try:
            _player.stop()
        except:
            self.log.exception('exception while stopping streams')
            

    def is_playing(self):
        return _player.is_playing()
