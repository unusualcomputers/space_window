from player_base import VideoPlayer
import logger
import os

class FilePlayer(VideoPlayer):
    def __init__(self,
            status_func=None,
            player=None,
            player_args=None):
        VideoPlayer.__init__(self,status_func,player,player_args)
    
    def _play_loop_impl(self,url,quality):
        try:
            subs=os.path.join(os.path.splitext(url)[0],'srt')
            if os.path.isfile(subs):
                cmd='%s "%s" --subtitles "%s"' % (self._player_cmd,url,subs)
            else:
                cmd='%s "%s"' % (self._player_cmd,url)

            while True:
                os.system(cmd)
        finally:
            pass
 
    def can_play(self,url):
        return os.path.isfile(url)

    def get_qualities(self,url):
        return ['best']