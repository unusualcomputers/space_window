from jsonable import Jsonable
import os
from html import build_html
from collections import OrderedDict
from video_player import Player
import threading
import logger
log=logger.get(__name__)

_streams_data='.space.window'
_base_path=os.path.join(os.path.expanduser('~'),_streams_data)
_config_path=os.path.join(_base_path,_streams_data)
_cnt=0 # global counter, used to make html more responsive

_player=None
# streams
#   main class managing sreams to play
class Streams(Jsonable):

    @classmethod
    def load(cls):
        if not cls.file_exists(_base_path):
            os.mkdir(_base_path)
        path=_config_path
        if cls.file_exists(path):
            s=cls.from_file(path)
            s.refresh_caches(False)
        else:
            s=cls()
            s.save()
        return s                

    def save(self):
        self.to_file(_config_path)
     
    def __init__(self,streams=OrderedDict()):
        self.streams=streams
        self.refresh_caches(True)

    def _get_data_for_first_video(self):
        if self.len() == 0: return
        (url,quality)=self.streams.items()[0][1]
        _player.can_play(url)

    def _get_data_for_rest(self):
        try:
            l=self.len()
            log.debug('GETTING REST %i',l)
            if l < 2: return
            for i in range(1,l):
                log.debug('GETTING: %s',self.streams.items()[i]) 
                (url,quality)=self.streams.items()[i][1]
                
                _player.can_play(url)
                log.debug('GOT %i %s',i,url)
        except:
            log.exception('exception while getting rest of videos')
            raise

    def refresh_caches(self,threaded=False):
        log.debug('INITIALISING PLAYER')
        global _player
        _player=Player()
        self._get_data_for_first_video()
        if threaded:
            threading.Thread(target=self._get_data_for_rest).start()        
        else:
            self._get_data_for_rest()

    def get_qualities(self,url):
        return _player.get_qualities(url)

    def len(self):
        return len(self.streams.items())

    def first(self):
        return self.at(0)

    def at(self,i):
        if i >= self.len():
            return None
        else:
            return self.streams.items()[i][0]
  	
    def next(self, name):
        for k in range(self.len()):
           if self.at(k)==name:
               return self.at(k+1)
        return self.at(0)

    def add(self, name, uri, quality):
        self.streams[name]=(uri,quality)
        threading.Thread(target=_player.can_play,
            args=(url))
        self.save()
        
    def remove(self,name):
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
            (uri,quality)=self.streams[name]
            row = u"""<tr><td>{}</td><td>{}</td><td>
                <input type="hidden" name="hidden_{}" value="{}">
                <button type="submit" name="action" value="play {}">
                    play
                </button></td><td>
                <button type="submit" name="action" value="moveup {}">
                    up</button></td>
                <td>
                <button type="submit" name="action" value="remove {}">
                        remove
                </button></td>
                <td><a href="{}" target="_blank"> Show in browser </a></td>
                </tr>
                """.format(name,quality,_cnt,name,name,name,name,uri)
            html+=row
        return html
        
    def play(self,name):
        (url,quality)=self.streams[name]
        _player.play(url,quality)

    def stop(self):
        try:
            _player.stop()
        except:
            log.exception('exception while stopping streams')
            

    def is_playing(self):
        return _player.is_playing()
