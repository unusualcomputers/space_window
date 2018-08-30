import pygame
from config_util import Config
import os

_screen=None

def pygame_init():
    pygame.display.init()
    pygame.font.init()
    pygame.mouse.set_visible(False)	

def screen():
    global _screen
    if _screen is None:
        pygame_init()
        config = Config('space_window.conf',__file__)    
        fbdev = config.get('pygame','fbdev','None')
        if fbdev != 'None':
            os.putenv('SDL_VIDEODRIVER','fbcon')
            os.environ["SDL_FBDEV"] = fbdev

        scrw=config.getint('pygame','screen_width',0)
        scrh=config.getint('pygame','screen_height',0)
        depth=config.getint('pygame','screen_depth',0)
    
        if depth==0:
            _screen=pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        else:
            _screen=pygame.display.set_mode((0,0),pygame.FULLSCREEN,depth)
    return _screen
