from streamlink_cli.main import *
from streamlink_cli.argparser import build_parser
from streamlink_cli.utils import NamedPipe
from streamlink_cli.output import PlayerOutput
from streamlink import Streamlink
import sys
from cache import SynchronisedCache as Cache
import threading
import time
import os
from contextlib import closing
from functools import partial
from itertools import chain

_player_cmd='omxplayer'
_player_args='--vol 500 --timeout 60'
#_player_cmd='mplayer -cache 8192'
#_player='mpv'
#_player_args=''
_player_cmd=_player_cmd+' '+_player_args
_default_res='360p'

_chunk_size=10240
_cache_size=50                               
class Streamer:
    def __init__(self):
        self.plugin_cache=Cache(_cache_size)
        self.streams_cache=Cache(_cache_size)
        self.streamlink=Streamlink()
        self.thread=None           
        self.playing=True
    
    def _create_output(self):
        pipename='unusualpipe={0}'.format(os.getpid())
        namedpipe=NamedPipe(pipename)
        return PlayerOutput(_player_cmd,args='{filename}',
            quiet=False,kill=True,namedpipe=namedpipe,http=None)

    def _open_stream(self,stream):
        stream_fd=stream.open()
        try:
            prebuffer=stream_fd.read(_chunk_size)
        except:
            stream_fd.close()
            raise 'Cannot read from stream'
        return stream_fd,prebuffer
        
    def _output_stream(self,stream):
        output=self._create_output()

        stream_fd,prebuff=self._open_stream(stream)
        output.open()
        with closing(output):
            stream_iterator = chain(
                [prebuff],
                iter(partial(stream_fd.read, _chunk_size), b"")
            )
            try:
                for data in stream_iterator:
                    if not self.playing: break
                    output.write(data)
            finally:
                stream_fd.close()
    
    def _get_streams(self, url):
        streams=self.streams_cache.get(url)
        if streams is None:
            streams=self.streamlink.streams(url)
            self.streams_cache.add(url,plugin)
        return streams
            
    def can_play(self,url):
        try:
            self.get_streams(url)
            return True
        except:
            return False

    def get_qualities(self,url):
        return self._get_streams(url).keys()
     
    def _play_thread(self,url, quality):
        try:
            streams=self._get_streams(url)
            if not streams: return
            stream=None
            if len(streams)==1:
                stream=streams.values()[0]
            elif quality in streams:
                stream=streams[quality]
            elif _default_res in streams:
                stream=streams[_default_res]
            elif 'best' in streams:
                stream=streams['best']
            if stream is not None:
                self._output_stream(stream)
        finally:
            self.playing=false
    
    def is_playing(self):
        return self.playing 
                   
    def play(self,url,quality):
        if self.is_playing():
            self.stop()
        self.playing=True
        self.thread=threading.Thread(
            target=self._play_thread, 
            args=(url,quality)).start()

    def stop(self):
        self.thread=None
        self.playing=False
        os.system('pkill -9 %s' % _player)
        time.sleep(0.1)#poor man's sychronisation
        os.system('pkill -9 %s' % _player)
