import pygame,sys
from pygame.locals import QUIT
import time
import threading
from config_util import Config
from weather import Weather
import os

class Clock:
    def __init__(self):
        config = Config('space_window.conf',__file__)    
        pygame.display.init()
        pygame.font.init()
        #size = width, height = 640, 480
        #self._screen = pygame.display.set_mode( size, 0 , 32 )
        self._screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN )
        
        self._forecol=config.getcolor('clock','foreground',(255,128,0))
        bckcol=config.getcolor('clock','background',(32,0,32))
        time_sz=config.getint('clock','time_size',192)
        date_sz=config.getint('clock','date_size',24)
        self._border=config.getint('clock','border',10)
        self._separation=config.getint('clock','separation',8)

        path=os.path.dirname(os.path.abspath(__file__))
        fontname = os.path.join(path,'digital-7_mono.ttf')
        self._time_font = pygame.font.Font( fontname, time_sz )
        self._secs_font = pygame.font.Font( fontname, time_sz/3 )
        self._date_font = pygame.font.Font( fontname, date_sz )
        self._black=self._screen.copy()
        self._black.fill(bckcol)
        width=self._screen.get_width()
        self.running=False    
        self._init_rects()

    def is_playing(self):
        return self.running

    def play(self):
        self.running=True
        threading.Thread(target=self._time_loop).start()
    
    def stop(self):
        self.running=False

    def _time_loop(self):
        cnt=0
        weather=Weather()
        self._update_weather(weather)
        while self.running:
            self._update_time()
            time.sleep(1)
            cnt+=1
            if cnt >3600:
                cnt=0
                self._update_weather(weather)

    def _update_weather(self,weather):
        w=weather.get()
        self._w_surface=self._date_font.render(w,True,self._forecol)
        self._w_rect=self._w_surface.get_rect()
        self._w_rect.top=self._d_rect.top
        screen_w=self._screen.get_rect().width
        self._w_rect.x=screen_w-self._border-self._w_rect.width
        
    def _init_rects(self):
        h_surface=self._time_font.render('88',True,self._forecol)
        m_surface=self._time_font.render('88',True,self._forecol)
        c_surface=self._time_font.render(':',True,self._forecol)
        s_surface=self._secs_font.render('88',True,self._forecol)
        d_surface=self._date_font.render('FRI, 88 JAN 8888',\
            True,self._forecol)
        
        self._h_rect=h_surface.get_rect()
        self._m_rect=m_surface.get_rect()
        self._c_rect=c_surface.get_rect()
        self._s_rect=s_surface.get_rect()
        self._d_rect=d_surface.get_rect()
        
        screen_rect=self._screen.get_rect()

        self._d_rect.top=self._border
        self._d_rect.x=self._border

        time_top=(screen_rect.height-self._h_rect.height+\
            self._d_rect.height+self._border)/2.0

        self._h_rect.top=time_top
        self._c_rect.top=time_top
        self._m_rect.top=time_top
        self._s_rect.bottom=self._m_rect.bottom
        
        time_width=self._h_rect.width+self._c_rect.width/3.0+\
            self._m_rect.width+self._separation+self._s_rect.width

        self._h_rect.x = self._border+(screen_rect.width-time_width)/2.0
        self._c_rect.x=self._h_rect.x+self._h_rect.width-self._c_rect.width/3.0
        self._m_rect.x=self._h_rect.x+self._h_rect.width+self._c_rect.width/3.0
        self._s_rect.x=self._m_rect.x+self._m_rect.width+self._separation        
    
    def _update_time(self):
        lt = time.localtime()
        d = time.strftime('%a, %d %b %Y')
        
        h = time.strftime('%H',lt)
        m = time.strftime('%M',lt)
        s = time.strftime('%S',lt)
        c = ':'
       
        if len(h)==0: return # when internet is poor, miss a beat
        h_surface=self._time_font.render(h,True,self._forecol)
        m_surface=self._time_font.render(m,True,self._forecol)
        c_surface=self._time_font.render(c,True,self._forecol)
        s_surface=self._secs_font.render(s,True,self._forecol)
        d_surface=self._date_font.render(d,True,self._forecol)
        self._screen.blit(self._black,(0,0))
        self._screen.blit(h_surface,self._h_rect)
        self._screen.blit(c_surface,self._c_rect)
        self._screen.blit(m_surface,self._m_rect)
        self._screen.blit(s_surface,self._s_rect)
        self._screen.blit(d_surface,self._d_rect)
        self._screen.blit(self._w_surface,self._w_rect)
        pygame.display.update()

if __name__=='__main__':
    clock=Clock()
    clock.play()
    while True:
        for evt in pygame.event.get():
            if evt.type == QUIT:
                clock.stop()
                time.sleep(2)
                pygame.quit()
                sys.exit()
        time.sleep(1)
