from streamlink_cli import *
import sys
from cache import SychronisedCache as Cache

#_player_cmd='omxplayer'
#_player_args='--vol 500 --timeout 60'
_player_cmd='mplayer -cache 2000'
_player_args='-cache 8192'

_cache_size=50                               
class Streamer:
    def __init__(
            self, 
            arguments=[
                '--player', '%s %s' %(_player_cmd,_player_args), 
                '--player-continuous-http']):
        self.plugin_cache=Cache(_cache_size)
        self.streams_cache=Cache(_cache_size)
        self.streamlink
        self.arglist=arguments  
        setup_streamlink()
        self.setup_args()
        setup_console(sys.stdout)
        self.thread=None           

        #setup_http_session()
    
    def setup_args(self):
        global args
        parser = build_parser()
        args,unknown=parser.parse_known_args(self.arglist)
        if args.stream:
            args.stream = [stream.lower() for stream in args.stream]
        if not args.url and args.url_param:
            args.url = args.url_param
        #setup_plugins(args.plugin_dirs)
        #setup_plugin_args(streamlink, parser)

    def _get_plugin(self,url):
        plugin=self.plugin_cache.get(url)
        if plugin is None:
            plugin=streamlink.resolve_url(url)
            self.plugin_cache.add(url, plugin)
        return plugin

    def can_handle(self,url):
        try:
            self.get_streams(url)
            return True
        except NoPluginError:
            return False

    def get_streams(self, url):
        global args #from streamlink_cli
        streams=self.streams_cache.get(url)
        if streams is None:
            args.url=url
            plugin=self._get_plugin(url)
            streams=fetch_streams(plugin)
            self.streams_cache.add(url,plugin)
        return streams
                
    def _play_thread(self,url, quality):
        if self.playing==True: return
        try:
            streams=get_streams(url)
            if not streams: return
            if quality in streams:
                plugin=self._get_plugin(url)
                handle_stream(plugin, streams,quality)
        finally:
            pass
    def is_playing(self):
        return (self.thread is not None) and self.thread.is_alive()
                   
    def play(self,url,quality):
        if (self.thread is not None) or self.thread.is_alive():
            self.stop()
        self.thread=\
            threading.Thread(self._play_thread, arguments=(url,quality)).start()

    def stop(self):
        self.thread=None
        os.system('pkill -9 %s' % _player_cmd)
        time.sleep(0.1)#poor man's sychronisation
        os.system('pkill -9 %s' % _player_cmd)
