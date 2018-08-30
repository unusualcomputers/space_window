from __future__ import unicode_literals
import pygame as pg
from time import *
import threading
import os
import sys
from config_util import Config
from borg import borg_init_once

class MsgScreenThread:
    def __init__(self,screen):
        config = Config('space_window.conf',__file__)    

        self._border=config.getint('message','border',10)
        self._left=config.getbool('message','left',False)
        self._top=config.getbool('message','top',False)
        self._forecol=config.getcolor('message','foreground',(255,128,0))
        bckcol=config.getcolor('message','background',(32,0,32))
        fontname=config.get('font','name','comicsansms')
        fontsz=config.getint('message','font_size',68)
        
        self.running=False
        self._delay=1
        self._screen=None
        self.text=None
        self.black=None
        self.font=None
        #sleep(1)
        pg.mouse.set_visible(False)	
        self.screen = screen
        self.black=self.screen.copy()
        self.black.fill(bckcol)
        self.font = pg.font.SysFont(fontname, fontsz)
        self.lock=threading.Lock()

    def lock_t(self):
        while not (self.lock.acquire(False)):
            sleep(0.1)
    
    def get_running(self):
        self.lock_t()
        r=self.running
        self.lock.release()
        return r

    def get_text(self):
        self.lock_t()
        t=self.text
        self.lock.release()
        return t

    def place_text(self):
        rows=self.get_text().split('\n')
        surfaces=[self.font.render(x,True,self._forecol) for x in rows]
        total_height=sum([s.get_height() for s in surfaces])
        avail_height=self.screen.get_height()-2*self._border
        while((total_height-surfaces[0].get_height())>avail_height):
            total_height-=surfaces[0].get_height()
            surfaces=surfaces[1:]
        rects=[s.get_rect() for s in surfaces]
        if self._top:
            top=self._border
        else:
            top = (self.screen.get_height()-total_height)/2.0
        width=self.screen.get_width()
        current_top=top
        for r in rects:
            r.top=current_top
            current_top=r.bottom
            if self._left:
                r.x=self._border
            else:
                r.x=(width-r.width)/2.0
        return zip(surfaces,rects)   
   
    def blank(self):
        self.screen.blit(self.black,(0,0))
         
    def run_msg(self):
        local_text=''
        while(self.get_running()):
            for event in pg.event.get():
                if event.type==pg.QUIT or \
                (event.type==pg.KEYDOWN and event.key==pg.K_c and \
                (pg.key.get_mods() & pg.KMOD_CTRL)):
                    print "ctrl-c pressed"
                    pg.quit()
                    sys.exit(0)
                    return
            if self.get_text()!=local_text:
                local_text=self.get_text()
                rows=self.place_text()
                self.screen.blit(self.black,(0,0))
                for row in rows:
                    self.screen.blit(row[0], row[1])
                pg.display.flip()
            sleep(self._delay)

class MsgScreen(borg_init_once):
    def __init__(self,screen):
        borg_init_once.__init__(self,screen)

    def init_once(self,screen):
        self._msg=MsgScreenThread(screen)

    def start_thread(self):
        if self._msg.get_running(): return
        self._msg.running = True
        threading.Thread(target=self._msg.run_msg).start()
    
    def lock_t(self):
        self._msg.lock_t()
    
    def stop(self):
        self.lock_t()
        self._msg.running=False
        self._msg.lock.release()

    def set_text(self,msg):  
        self.lock_t()
        self._msg.text=msg
        self._msg.lock.release()
        self.start_thread()

    def get_text(self):
        self.lock_t()
        t=self._msg.text
        self._msg.lock.release()
        return t

    def blank(self):
        self.lock_t()
        t=self._msg.blank()
        self._msg.lock.release()
         
