import streamer
from time import sleep
import os
print __file__
print os.path.dirname(__file__)
url='https://www.youtube.com/watch?v=XOacA3RYrXk'
#url='https://www.youtube.com/watch?v=XbZjFCGZ1Mc'
#url='https://youtu.be/RtU_mdL2vBM'
s=streamer.Streamer()
#print s.can_play(url)
#print s.get_streams(url)
#print s.streamlink.streams(url)
print s.get_qualities(url)
s.play(url,'360p')
print 'playing'
sleep(20)
print 'stopping'
s.stop()

url='https://www.youtube.com/watch?v=XbZjFCGZ1Mc'
s.play(url,'360p')
print 'playing'
sleep(20)
print 'stopping'
s.stop()
