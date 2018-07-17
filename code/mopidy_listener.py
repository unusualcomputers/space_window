from mopidy_json_client import MopidyClient
import wifi_setup_ap.wifi_control as wifi
from wifi_setup_ap.wifi_control import run
import logger
import subprocess

class MopidyUpdates:
    def __init__(self,updates_func):
        ps=run('ps -e')
        if ps.find('opidy') == -1:
            subprocess.Popen(['mopidy'])             
        ip=wifi.get_ip()
        ws_url='ws://%s:6680/mopidy/ws' % ip
        self._update_func=updates_func
        self._mopidy=MopidyClient(ws_url=ws_url)
        self._mopidy.bind_event('track_playback_started', self.playback_started)
        self._mopidy.bind_event('stream_title_changed', self.title_changed)
        self._show_updates=False
        self.log=logger.get(__name__)

    def update(self,msg):
        if self._show_updates:
            self._update_func(msg)

    # mopidy updates
    def playback_started(self,tl_track):
        try:
            track=tl_track.get('track') if tl_track else None
            if not track:
                return
            trackinfo={
                'name' : track.get('name'),
                'artists': ', '.join(\
                    [artist.get('name') for artist in track.get('artists')])
            }
            txt = u'{artists}\n{name}'.format(**trackinfo)
            self.update(txt)
        except: 
            self.log.exception('in playback started')
            pass

    def title_changed(self,title):
        try:
            self.update(title)
        except:
            self.log.exception('in title changed')
            pass

    def show_updates(self):
        self._show_updates=True

    def stop(self):
        try:
            self._mopidy.playback.stop()
        except:
            self.log.exception('error stopping mopidy')
        finally:
            self._show_updates=False
