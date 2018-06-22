from video_player import Player
from time import sleep


vp=Player()
urls=[('https://www.youtube.com/watch?v=X7tqytcVS-4','360p'),('https://www.youtube.com/watch?v=yBca1ixoEbg&index=5&list=RDrdVXn8a5k0Q','360p'),('http://www.ustream.tv/petespond','best'),('https://www.twitch.tv/tsm_myth','360p')]

for url,quality in urls:
    print 'trying ',url,quality
    can_play=vp.can_play(url)
    print 'can play ',can_play
    qualities=vp.get_qualities(url)
    print 'qualities ',qualities
    #vp.play(url,quality)
    #sleep(60)
    #print 'stopping'
    #vp.stop()

