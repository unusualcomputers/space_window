from __future__ import unicode_literals
import os
from os.path import *
import random
import logger
from html import build_html,get_empty_html
from time import sleep
import threading
from config_util import Config
import subprocess

_log=logger.get(__name__)
_cnt=random.randint(0,1000)

_music_form=u"""
        <div align="left">
        <form align="center" action="/music_list">
        <table width=100%>
        [%MUSIC_ROWS%]
        <tr>
        <td>
        <button type="submit" name="action" value="musicplayall">
                        Play all
        </button>
        </td><td>
        <button type="submit" name="action" value="musicshuffleall">
                        Shuffle all
        </button>
        </td><td>
        <button type="submit" name="action" value="musicremove">
                        Remove selected
        </button>
        </td>
        </table>
        </form></div>
        <br/>
        <hr/>
        <br/>
       <form enctype="multipart/form-data" action="/upload_music" method="post"> 
        Music to upload<br/> 
        Folder to upload to <input type="text" name="foldername" value=""><br/>
        <input type="file" accept="audio/*" name = "music" multiple/>
        <p><input type="submit" value="Upload" style="width:15%;"></p>
        </form>
        """

class Music:
    def __init__(self,status_update_func):
        self._status_update=status_update_func    
        self.path=join(dirname(abspath(__file__)),'music')
        if not isdir(self.path): os.mkdir(self.path)
        self.files_data=[]#(name,is_folder,full_path) 
        self._running=False
        self.lock=threading.Lock()
        self.reload_config()

    def reload_config(self):
        config = Config('space_window.conf',__file__)    
        self._player=config.get('player','player','omxplayer')
       
        self._player_args=config.get('player','player_args',
            ' --timeout 60 --loop --no-osd -b').replace('-b','')
        self._player_pl_args=config.get('player','playlist_player_args',
               ' --timeout 60 --no-osd -b').replace('-b','')
        
        self._player_cmd=self._player+' '+self._player_args
        self._player_pl_cmd=self._player+' '+self._player_pl_args
    
    def _make_html_row(self,is_folder,name,i):
        global _cnt
        _cnt+=1
        
        if is_folder is False:
            return u"""
        <tr>
        <td></td>
        <td>%s</td>
        <td>
        <input type="hidden" name="hidden_%s" value="%s">
        <input type="checkbox" name="remove_music_%s" value="%s">
        <td>
        <td>
        <button type="submit" name="action" value="play_music %s">
                        Play
        </button></td>
        </tr>
        """ % (name,_cnt,name,i,i,i)
        else:
            return u"""
        <tr>
        <td>%s</td>
        <td></td>
        <td>
        <input type="hidden" name="hidden_%s" value="%s">
        <input type="checkbox" name="remove_music_%s" value="%s">
        <td>
        <td>
        <button type="submit" name="action" value="play_music %s">
                        Play
        </button></td>
        </tr>
        """ % (name,_cnt,name,i,i,i)
        

    def _reload_files(self):
        self.files_data=[]#(name,is_folder,full_path) 
        for root,d,files in os.walk(self.path):
            self.files_data.append((root,True,root))
            for f in files:
                p=join(root,f)
                self.files_data.append((f,False,p))

    def refresh(self):
        with self.lock:
            self._reload_files()

    def make_html(self):
        self._reload_files()
        i=0
        rows=[]
        for name,is_folder,path in self.files_data:
           rows.append(self._make_html_row(is_folder,name,i))
           i+=1
        html=_music_form.replace('[%MUSIC_ROWS%]',"".join(rows))
        return get_empty_html(html)

    def make_remove_html(self,csvindices):
        global _cnt
        _cnt+=1
        form = u"""    
            <p style="font-size:45px">Really remove all these files?</p>

            <form action="/really_remove_music">
            <input type="hidden" name="hidden_{}" value="{}">
            <button type="submit" name="action" value="really remove {}">
                    Yes, really remove them!
            </button></td><td>
            </form>
        """.format(_cnt,csvindices,csvindices)
        return build_html(form)
    
    def remove(self,csvindices):
        if self.is_playing():
            self.stop()
        to_remove=[int(i) for i in csvindices.split(',')]
        for i in to_remove:
            if self.file_data[i][1]:#folder
                j=i+1
                while j<len(self.files_data) and not self.files_data[j][1]:
                    path=self.files_data[j][2]
                    j+=1           
                    if exists(path): os.remove(path)
        
                path=self.files_data[i][2]
                if exists(path): os.rmdir(path)
            else:
                path=self.files_data[i][2]
                if exists(path): os.remove(path)
        self._reload_files()
            
    def is_playing(self):
        return self._running

    def play(self,shuffle,i):
        if len(self.files_data)<1:
            return
        if self._running: return
        self._running=True
        threading.Thread(target=self._music,args=(i,shuffle)).start()

    def stop(self):
        self._running=False
        os.system('pkill -9 %s' % self._player)
        sleep(1)
        os.system('pkill -9 %s' % self._player)
        
    def _music(self,i,shuffle):    
        try:
            playlist=[]
            with self.lock: 
                if len(i)==0:
                    for name, is_folder, path in self.files_data:
                        if not is_folder:
                            playlist.append((name,path))
                elif len(i)==1 and self.files_data[i[0]][1]:
                    j=i[0]+1
                    while j<len(self.files_data) and not self.files_data[j][1]:
                        m=self.files_data[j]
                        j+=1
                        playlist.append((m[0],m[2]))
                elif len(i)==1:
                    m=self.files_data[i[0]]
                    playlist.append((m[0],m[2]))
                else:
                    idxs=[]
                    for ii in i:
                        if self.files_data[ii][1]:#folder
                            j=i[0]+1
                            while j<len(self.files_data) and \
                                not self.files_data[j][1]:
                                if j not in idxs: idxs.append(j)
                        else:
                            if ii not in idxs: idxs.append(ii)
                    for idx in idxs:
                        m=self.files_data[idx]
                        playlist.append((m[0],m[2]))
    
         
            if shuffle:
                random.shuffle(playlist)

            if len(playlist)==1:
                cmd='%s "%s"' % (self._player_pl_cmd,playlist[0][1])
                subprocess.call(cmd,shell=True)
            else:
                for name,path in playlist:
                    if not self._running: 
                        return
                    cmd='%s "%s"' % (self._player_cmd,path)
                    subprocess.call(cmd,shell=True)
        except:
            self._running=False
            _log.exception('exception in music player')
            raise


