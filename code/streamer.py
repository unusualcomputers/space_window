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
from player_base import VideoPlayer

_default_res='360p'
_chunk_size=10240
_cache_size=50                               

class Streamer(VideoPlayer):
    def __init__(self,
            status_func=None,
            player=None,
            player_args=None):
        VideoPlayer.__init__(self,status_func,player,player_args)
        self.plugin_cache=Cache(_cache_size)
        self.streams_cache=Cache(_cache_size)
        self.streamlink=Streamlink()
    
    def _create_output(self):
        pipename='unusualpipe={0}'.format(os.getpid())
        namedpipe=NamedPipe(pipename)
        return PlayerOutput(self._player_cmd,args='{filename}',
            quiet=False,kill=True,namedpipe=namedpipe,http=None)

    def _open_stream(self,stream):
        self._status('buffering...')
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
        self._status('preparing player...')
        output.open()
        with closing(output):
            stream_iterator = chain(
                [prebuff],
                iter(partial(stream_fd.read, _chunk_size), b"")
            )
            try:
                self._status('playing :)')
                for data in stream_iterator:
                    if not self.playing: break
                    output.write(data)
            finally:
                stream_fd.close()
    
    def _get_streams(self, url):
        self._status('getting stream information.\n'+
            'do be patient,\nthis is a true miracle of technology.')
        streams=self.streams_cache.get(url)
        if streams is None:
            streams=self.streamlink.streams(url)
            self.streams_cache.add(url,plugin)
        return streams
            
    def get_qualities(self,url):
        return self._get_streams(url).keys()
     
    def _play_loop_impl(self,url, quality):
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
    
