from streamlink_cli.utils import NamedPipe
from streamlink_cli.output import PlayerOutput
from streamlink import Streamlink
from cache import SynchronisedCache as Cache
import time
import os
from functools import partial
from itertools import chain
from player_base import VideoPlayer
import threading 
import thread
import logger

log=logger.get(__name__)

_default_res='360p'
_chunk_size=10240
_cache_size=50                               

class Streamer(VideoPlayer):
    def __init__(self,
            status_func=None,
            player=None,
            player_args=None):
        VideoPlayer.__init__(self,status_func,player,player_args)
        self.streams_cache=Cache(_cache_size)
        self.streamlink=Streamlink()
        #check if this works for multiple streams
        self._output=self._create_output()
        self.lock=threading.Lock()
        self.alive_threads=[]
    
    
    def _make_pipe(self,cnt=10):
        try:
            pipename='unusualpipe={}{}'.format(os.getpid(),cnt)
            return NamedPipe(pipename)
        except OSError:
            if cnt>0:
                return self._make_pipe(cnt-1)
            else:
                raise
      
    def _create_output(self):
        namedpipe=self._make_pipe()
        return PlayerOutput(self._player_cmd,args='{filename}',
            quiet=False,kill=True,namedpipe=namedpipe,http=None)

    def _open_stream(self,stream):
        self._status('buffering...')
        try:
            stream_fd=stream.open()
            prebuffer=stream_fd.read(_chunk_size)
        except:
            stream_fd.close()
            raise Exception('Cannot read from stream')
        return stream_fd,prebuffer
        
    def _output_stream(self,stream):
        try:        
            with self.lock:
                thread_id=thread.get_ident()
                self.alive_threads.append(thread_id)
            stream_fd,prebuff=self._open_stream(stream)
            self._status('preparing player...')
            self._output.open()
            stream_iterator = chain(
                [prebuff],
                iter(partial(stream_fd.read, _chunk_size), b"")
            )
            self._status('playing :)')
            for data in stream_iterator:
                with self.lock:
                    if thread_id not in self.alive_threads: break
                self._output.write(data)
        except:
            log.exception('exception while outputing stream')
        finally:
            try:
                stream_fd.close()
                self._output.close()
            except:
                log.exception('exception while closing streams')

    def _get_streams(self, url):
        streams=self.streams_cache.get(url)
        if streams is None:
            self._status('getting stream information.\n'+
                'do be patient,\nthis is a true miracle of technology.')
            streams=self.streamlink.streams(url)
            self.streams_cache.add(url,streams)
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
        elif 'worst' in streams:
            stream=streams['worst']
        
        if stream is not None:
            self._output_stream(stream)
    
    def _stop_threads(self):
        with self.lock:
            self.alive_threads=[]

