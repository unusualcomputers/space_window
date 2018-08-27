import requests
from random import *
import io
import pygame as pg
from time import *
import threading
import os
import sys
import logger
from config_util import Config
#os.putenv('SDL_VIDEODRIVER','fbcon')
#os.putenv('SDL_FBDEV','/dev/fb0')

_log=logger.get(__name__)
class NasaPod:
    def __init__(self):
        self._apod_url='https://apod.nasa.gov/apod/'
        self._apod_archive_url='https://apod.nasa.gov/apod/archivepix.html'
        # delay between frames in seconds
        self._running=False
        pg.display.init()
        pg.font.init()
        self.load_config()

    def load_config(self):
        config = Config('space_window.conf',__file__)    
        self._delay=config.getint('nasa','frame_delay',5) 
        self._fontname=config.get('font','name','comicsansms')
        self._fontsize=config.getint('nasa','font_size',48)
        self._font = pg.font.SysFont(self._fontname,self._fontsize)
        self._text_col=config.getcolor('nasa','foreground',(100,100,100))
        self._text_height_ratio=config.getint('nasa','height_ratio',10)        

    def _build_list(self):
        html = requests.get(self._apod_archive_url).content
        s=html.find("<b>")
        e=html.find("</b>")
        pages=filter(lambda x:'<a href="' in x,html[s:e].split('\n'))
        return pages

    def _load_at_index(self,x,pages,scrw,scrh):
        l=pages[x]
        t=l.split(':')
        uri=self._apod_url+t[1].split('"')[1]
        html=requests.get(uri).content
        s=html.find('<IMG SRC="')
        if s != -1:    
            l=len('<IMG SRC="')
            e=html.find('"',s+l)
            uri=self._apod_url+html[s+l:e]
            date=t[0]
            name=t[1].split('>')[1].split('<')[0]
            image_file = io.BytesIO(requests.get(uri).content)
            image = pg.image.load(image_file)
            h=image.get_height()
            w=image.get_width()
            sw=h/float(scrh)
            sh=w/float(scrw)
            s=max(sh,sw)
            h=int(h/s)
            w=int(w/s)
            #print s, w,h
            image=pg.transform.scale(image,(w,h)).convert()
            return (name, date, image)
        else:
            return None
            
    def _load(self,x,pages,scrw,scrh):
        r=self._load_at_index(x,pages,scrw,scrh)
        if r is not None: return r
        l=len(pages)
        if x >=l: x=0
        else: x+=1
        return self._load(x,pages,scrw,scrh)
     
    def _place_text(self,p,y=0,pref="",screen=None):
        text = self._font.render(pref+p[0], True,self._text_col)
        textrect = text.get_rect()
        textrect.centerx = screen.get_rect().centerx
        textrect.centery = screen.get_height()/self._text_height_ratio+y
        return (text,textrect)

    def _end_loop(self,black,screen):
        black.set_alpha(255)
        black.fill((0,0,0))
        screen.blit(black,(0,0))
        pg.display.flip()
        self._running=False

    def _slideshow(self):    
        try:
            pg.display.init()
            pg.font.init()
            pg.mouse.set_visible(False)	
            screen = pg.display.set_mode((0,0),pg.FULLSCREEN )
            scrh=screen.get_height()
            scrw=screen.get_width()
            black=screen.copy()
            black.fill((0,0,0))
            blackalpha=screen.copy()
            blackalpha.fill((0,0,0))

            (text,textrect)=self._place_text(("loading first image",""),
                screen=screen)
            screen.blit(text, textrect)
            pg.display.flip()

            pages=self._build_list()
            self._running=True
            p=self._load(0, pages,scrw,scrh) 
            prev_p=None
            t0=time()-self._delay
            screen.blit(black,(0,0))
            pg.display.flip()
            while self._running:
                for event in pg.event.get():
                    if event.type==pg.QUIT or \
                        (event.type==pg.KEYDOWN and event.key==pg.K_c and \
                        (pg.key.get_mods() & pg.KMOD_CTRL)):
                        pg.quit()
                        raise SystemExit
                t1=time()
                if t1-t0 < self._delay: continue
                t0=t1
                if prev_p is not None:
                    image = prev_p[2]
                    ih=image.get_height()
                    iw=image.get_width()
                    x=(scrw-iw)/2
                    y=(scrh-ih)/2
                    (text,textrect)=self._place_text(prev_p,screen=screen)
                    (nt,ntr)=self._place_text(p,40,"Next: ",screen=screen)
                    black.blit(text, textrect)
                    black.blit(nt, ntr)
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
                image = p[2]
                ih=image.get_height()
                iw=image.get_width()
                x=(scrw-iw)/2
                y=(scrh-ih)/2
                if prev_p is None: prev_p=p
                (text,textrect)=self._place_text(prev_p,screen=screen)
                (nt,ntr)=self._place_text(p,40,"Next: ",screen=screen)
                screen.blit(black,(0,0))
                screen.blit(text, textrect)
                screen.blit(nt, ntr)
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
                p=self._load(randint(1,len(pages)-1),pages,scrw,scrh)
            self._end_loop(black,screen)
        except:
            self._running=False
            _log.exception('exception in nasa pod slideshow')
            self._place_text('something is wrong with nasa pod :('
                ,screen=screen)
            raise

    def is_playing(self):
        return self._running

    def play(self):
        if self._running: return
        self._running=True
        threading.Thread(target=self._slideshow).start()

    def stop(self):
        self._running=False

if __name__=="__main__":    
    try:
        apod=NasaPod()
        apod.play()
    except:
        _log.exception('nasa pod main')
    finally:
        pg.quit()

