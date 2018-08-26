import glob
import os
from os.path import *
import pygame as pg
import random
import re
from config_util import Config
from time import *
import threading
import logger
from html import build_html,get_empty_html
from time import sleep

_log=logger.get(__name__)
_cnt=random.randint(0,1000)
_pic_form="""
        <div align="left">
        <form align="center" action="/gallery_list">
        <table width=100%>
        [%PIC_ROWS%]
        <tr>
        <td></td><td>
        <button type="submit" name="action" value="picremove">
                        Remove selected
        </button>
        </td>
        </table>
        </form></div>
        <br/>
        <hr/>
        <br/>
        <form enctype="multipart/form-data" action="/upload_pic" method="post"> 
        Picture 
        <input type="file" accept="image/jpeg" name = "picture" multiple/>
        <p><input type="submit" value="Upload"></p>
        </form>
        """
class Gallery:
    def __init__(self,status_update_func):
        config = Config('space_window.conf',__file__)    
        self._delay=config.getint('gallery','frame_delay',10) 
        self.thumb_sz=64
        
        self._status_update=status_update_func    
        self.path=join(dirname(abspath(__file__)),'photos')
        self.thumbspath=join(self.path,'thumbnails')
        if not isdir(self.path): os.mkdir(self.path)
        if not isdir(self.thumbspath): os.mkdir(self.thumbspath)
        pg.display.init()
        self._load_files()
        self._running=False
    
    def _make_thumb_path(self,picpath):
        picfile,picext = splitext(basename(picpath))
        thumbfile=picfile+'_thumb'+picext
        return join(self.thumbspath,thumbfile)
        
    def _make_thumb(self,picpath,pic):
        thumb_path=self._make_thumb_path(picpath)
        if isfile(thumb_path):
            return pg.image.load(thumb_path)
        w=pic.get_width()
        h=pic.get_height()
        sw=w/float(self.thumb_sz)
        sh=h/float(self.thumb_sz)
        s=max(sw,sh)
        h=int(h/s)
        w=int(w/s)
        thumb=pg.transform.scale(pic,(w,h)).convert()
        pg.image.save(thumb,thumb_path)
        return thumb

    def _resize_pic(self,pic,scrw, scrh):
        w=pic.get_width()
        h=pic.get_height()
        sw=w/float(scrw)
        sh=h/float(scrh)
        s=max(sw,sh)
        h=int(h/s)
        w=int(w/s)
        return pg.transform.scale(pic,(w,h)).convert()
    
    def _load_files(self):
        screen = pg.display.set_mode((0,0),pg.FULLSCREEN )
        scrh=screen.get_height()
        scrw=screen.get_width()
        pictures=glob.glob(join(self.path,'*.*'))
        pictures.sort()
        self.images=[]
        for p in pictures:
            try:
                pic=pg.image.load(p)
            except:
                continue
            pic=self._resize_pic(pic,scrw,scrh)
            thumb=self._make_thumb(p,pic)
            thumb_path=self._make_thumb_path(p)
            with open(p) as pf:
                pic_read=pf.read()
            with open(thumb_path) as tf:
                thumb_read= tf.read()
            self.images.append((p,thumb_path,pic,thumb,pic_read,thumb_read))
   
    def remove_several(self,picpaths):
        for picpath in picpaths:
            if exists(picpath): os.remove(picpath)
            tpath=self._make_thumb_path(picpath)
            if exists(tpath):os.remove(tpath)
        self._load_files()
        self._rename_files()
    
    def remove(self,picpath):
        if exists(picpath): os.remove(picpath)
        tpath=self._make_thumb_path(picpath)
        if exists(tpath):os.remove(tpath)
        self._load_files()
        self._rename_files()
 
    def _make_file_name(self,fname,i):
        nm,ext=splitext(basename(fname))
        return ('%05d_IMG%s' % (i,ext))               

    def _rename_files(self):
        sz=len(self.images)
        renamed=[]        
        for i in range(0,sz):
            curr_name=self.images[i][0]
            new_name=join(self.path,self._make_file_name(curr_name,i))
            if curr_name != new_name:
                os.rename(curr_name,new_name+'.tmp')
                renamed.append(new_name+'.tmp')
                curr_th_name=self.images[i][1]
                new_th_name=join(self.thumbspath,
                        self._make_file_name(curr_th_name,i))
                os.rename(curr_th_name,new_th_name+'.tmp')
                renamed.append(new_th_name+'.tmp')
                ii=self.images[i]
                self.images[i]=(new_name,new_th_name,ii[2],ii[3],ii[4],ii[5])
   
        for r in renamed:
            nr=r[:-4]
            os.rename(r,nr)

    def move_up(self, fname):
        sz=len(self.images)
        if sz < 2: return
        if self.images[0][0]==fname:return
        prev=self.images[0]
        for i in range(1,sz):
            current=self.images[i]
            if current[0]==fname:
                playing=self.is_playing()
                if playing: self.stop()
                self.images[i-1]=current
                self.images[i]=prev
                self._rename_files()
                if playing: self.play()
                return
            prev=current

    def add_several(self,fnames):
        i=len(self.images)
        for fname in fnames:
            name=self._make_file_name(fname,i)
            picpath=join(self.path,name)
            os.rename(fname,picpath)
            i+=1
        self._load_files()

    def add(self,fname):
        i=len(self.images)
        name=self._make_file_name(fname,i)
        picpath=join(self.path,name)
        os.rename(fname,picpath)
        self._load_files()

    def is_pic(self,fpath):
        for i in self.images:
            if i[0] == fpath or i[1] == fpath: 
                return True
        return False

    def serve_pic(self,fpath):
        for i in self.images:
            if i[0]==fpath: return i[4]
            if i[1]==fpath: return i[5]
        return None
 
    def _make_html_row(self,picpath,thumb_path):
        global _cnt
        _cnt+=1
        return """
        <tr>
        <td><a href="%s"><img src=%s></a></td>
        <td>
        <input type="hidden" name="hidden_%s" value="%s">
        <input type="checkbox" name="remove_pic_%s" value="%s">
        <td>
        <button type="submit" name="action" value="picup %s">
                        up
        </button></td>
        </tr>
        """ % (picpath,thumb_path,_cnt,picpath,picpath,picpath,picpath)

    def make_html(self):
        rows=[self._make_html_row(p[0],p[1]) for p in self.images]
        html=_pic_form.replace('[%PIC_ROWS%]',"".join(rows))
        return get_empty_html(html)

    
    def make_remove_html(self,fname):
        global _cnt
        _cnt+=1
        form = u"""    
            <p style="font-size:45px">Really remove all these pictures?</p>

            <form action="/really_remove_pic">
            <input type="hidden" name="hidden_{}" value="{}">
            <button type="submit" name="action" value="really remove {}">
                    Yes, really remove them!
            </button></td><td>
            </form>
        """.format(_cnt,fname,fname)
        return build_html(form)
    
    def is_playing(self):
        return self._running

    def play(self):
        if len(self.images)<1:
            self._status_update('Please upload some pictures to the gallery')
            return
        if self._running: return
        self._running=True
        threading.Thread(target=self._slideshow).start()

    def stop(self):
        self._running=False


    def _end_loop(self,black,screen):
        black.set_alpha(255)
        black.fill((0,0,0))
        screen.blit(black,(0,0))
        pg.display.flip()
        self._running=False

    def _slideshow(self):    
        try:
            if len(self.images)<1:return
            self._running=True
            pg.mouse.set_visible(False)	
            screen = pg.display.set_mode((0,0),pg.FULLSCREEN )
            scrh=screen.get_height()
            scrw=screen.get_width()
            black=screen.copy()
            black.fill((0,0,0))
            blackalpha=screen.copy()
            blackalpha.fill((0,0,0))

            prev_p=None
            t0=time()-self._delay
            screen.blit(black,(0,0))
            pg.display.flip()
            idx=0
            while self._running:
                t1=time()
                if t1-t0 < self._delay: 
                    sleep(0.5)
                    continue
                t0=t1
                p=self.images[idx][2]
                idx+=1
                if idx==len(self.images): idx=0
                if prev_p is not None:
                    image = prev_p
                    ih=image.get_height()
                    iw=image.get_width()
                    x=(scrw-iw)/2
                    y=(scrh-ih)/2
                    #fading out
                    for i in range(0,255,1):
                        if not self._running: 
                            self._end_loop(black,screen)
                            return
                        #sleep(0.02)
                        image.set_alpha(255-i)
                        blackalpha.set_alpha(255-i)
                        screen.blit(black,(0,0))
                        screen.blit(blackalpha,(0,0))
                        screen.blit(image,(x,y))
                        pg.display.flip()
                    black.fill((0,0,0))
                image = p
                ih=image.get_height()
                iw=image.get_width()
                x=(scrw-iw)/2
                y=(scrh-ih)/2
                screen.blit(black,(0,0))
                # fading in
                for i in range(0,255,1):
                    if not self._running: 
                        self._end_loop(black,screen)
                        return
                    #sleep(0.02)
                    image.set_alpha(i)
                    blackalpha.set_alpha(i)
                    screen.blit(blackalpha,(0,0))
                    screen.blit(image,(x,y))
                    pg.display.flip()
                screen.blit(black,(0,0))
                image.set_alpha(255)
                black.fill((0,0,0))
                screen.blit(image,(x,y))
                pg.display.flip()
                prev_p=p
            self._end_loop(black,screen)
        except:
            self._running=False
            _log.exception('exception in nasa pod slideshow')
            raise

