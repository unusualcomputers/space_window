from player_base import VideoPlayer
import logger
import os
from os.path import *
import time
from wifi_control import run

_log=logger.get(__name__)

class FilePlayer(VideoPlayer):
    def __init__(self,
            status_func=None):
        VideoPlayer.__init__(self,status_func)

    def _play_loop_impl(self,url,quality):
        try:
            subs=os.path.splitext(url)[0]+'.srt'
            if os.path.isfile(subs):
                cmd='%s "%s" --subtitles "%s"' % (self._player_cmd,url,subs)
            else:
                cmd='%s "%s"' % (self._player_cmd,url)
            _log.info('omx command: '+cmd)
            while self.playing:
                os.system(cmd)
        finally:
            pass
 
    def can_play(self,url):
        return os.path.isfile(url)

    def get_qualities(self,url):
        return ['best']
