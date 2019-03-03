Space window is like a picture that shows faraway places.

It will stream videos from the internet or play your own ones, show beautiful pictures of space that NASA publishes every day or some you chose yourself, play radio and podcasts and show time and weather where you are. You control it via an internet browser.

If it is not connected to the internet it will create its own standalone network so that you can still reach it and configure a WiFi connection or just upload videos, music and pictures that it will then play for you. 

It is friendly and when you switch it on it will tell you what it is doing and how to connect to it.
 
## How to use it

Space window creates a small website through which you can control it: 

![space window browser](https://github.com/unusualcomputers/space_window/blob/master/pics/sw_browser_home.png)

There is a video screen capture of it [here](https://www.youtube.com/watch?v=9pF4ZKuxq8o&t=36s).

In the list at the top are videos, you can add links to online streams or youtube clips and playlists or upload your own. If your network is very slow you can specify quality of the videos you want to stream. We rely on [streamlink](https://github.com/streamlink/streamlink) so the full list of online streams that would work is in [streamlink documentation](https://streamlink.github.io/plugin_matrix.html).

 * Nasa POD   
   
   Clicking this will connect to Nasa and start a slideshow of their picture of the day, first showing today's one and then going through all the other thousands of them in a random order. 

* Radio
  
   Radio opens a new tab showing [Mopidy](https://www.mopidy.com/) control page. Here the world is your oyster - it will play thousands of internet radio stations, podcasts, streams from MixCloud and so on. Radio will happily work together with stuff that doesn't play videos on screen - Nasa pictures, clock, photo gallery.

* Clock

  This button turns space window into an old fashioned digital clock. It will also show the weather where you are or where you configure it to - it gets this from wonderful [yr.no](https://www.yr.no/) site and will cover most of the world.

* Photo Gallery

    A slideshow of your pictures, when you click this it will show you the list of them in the browser and let you add more.  

* Play next

    Plays next.

* Upload video

    You can upload films and subtitles for them.

* Upload music

    If you want mopidy to play your local music files you can upload them here.

* Configuration

    There are quite a few options here - fonts, colors, slideshow speed, location for the clock and weather display and so on. Definitely worth checking out.


The bottom row of buttons is for maintenance, you'll use it rarely if ever, but they are handy (Update most of all, this is how we will fix bugs you tell us about).




## Hardware


Most of the magic is in software and it will run just fine on Pi Zero - a bigger Pi would work of course, though it would be wasteful. Apart from the computer you will need a screen of some kind, some way for raspberry to reproduce sound would be nice and a connection to internet helps, though even without it picture slideshows, uploaded music and videos would work fine. 

Our first one used a nice 10.1'' lcd from banggood, [the second one](https://github.com/unusualcomputers/space_window/blob/master/code/RockI.md) a 4'' Waveshare screen. The big lcd we used came with a board that had separate 3.5mm audio output so sound was easy, but I2S audio DAC and a usb sound card work a charm too. Finally you'll need a way to connect to the internet. Pi Zero W built in WiFi works well, though in our models we used plain old Pi Zero with a short cable and Edimax dongle in order to get the dongle out in the clear to improve reception (one thing you want to try and get right is a nice strong WiFi reception). Of course you will need a power supply, how mighty it should be will depend mostly on your choice of the screen, for our big 10'' lcd version we use a 2.5A one, the small rock computer works fine with 1A.

![sw1](https://github.com/unusualcomputers/space_window/blob/master/pics/space1.jpg) ![sw2](https://github.com/unusualcomputers/space_window/blob/master/pics/space3.jpg) 
![sw3](https://github.com/unusualcomputers/space_window/blob/master/pics/space4.jpg) ![swback](https://github.com/unusualcomputers/space_window/blob/master/pics/spaceW%20back1.jpg)


All in all, you need to put together a Raspberry Pi based machine that can connect to internet and, if you can, have some way to play music. If you are using usb sound cards or I2S dacs make sure alsa playback works on its own, once that is configured you can set it up in space window configuration page.

It should all run from a Raspbian Lite installation, window managers would just slow things down and are not used at all. There is so much information and good advice around on how to get this going in various configurations that almost anything you can think of can be made to work. Let us know if you need help figuring any of this out.


## Installation

To start with you need to install [Raspbian Lite](https://www.raspberrypi.org/downloads/raspbian/) and connect it to the internet (this depends quite a bit on your choice of hardware, but for WiFi [this will work](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md). It is nice to change the name of your new computer because that is how you will be finding on the network, we called ours SpaceWindow so to get to it we type spacewindow.local in a browser, this is easily done using [raspi-config](https://www.raspberrypi.org/documentation/configuration/raspi-config.md).

Once all that is ready and you can connect to your raspberry terminal, download and run [this script](https://raw.githubusercontent.com/unusualcomputers/space_window/master/code/space_window_install.sh), for example:

```
 wget https://raw.githubusercontent.com/unusualcomputers/space_window/master/code/space_window_install.sh
 sudo chmod a+x ./space_window_install.sh
 sudo ./space_window_install.sh
```

The script installs a whole bunch of things, it's pretty easy to read if you want to find out what, but in short all of it is software used to run our code provided by good people of the internet and nothing else. It takes a while, about half an hour or more on Pi Zero.

In most cases things would just work after you installed the code, and you can tweak much of the behaviour using the browser.
Just reboot and watch the screen, it will tell you how to connect to it (basically type in the_name_of_your_machine.local in a browser on some computer on the same network, default is rapberrypi.local, ours is spacewindow.local).  


### Configuration

If your hardware is unusual though, you may need to do some manual configuration. All configuration is in a file space_window/code/space_window.conf wherever you installed the software.

#### GPIO screens

 If you are using a GPIO screen you will need a bit of extra magic. Find the section [pygame] in this file. Here you will need to configure fbdev variables. For most screens you just need to set fbdev to /dev/fb1 and then the screen size and color depth (check [this](https://github.com/notro/fbtft/wiki/Pygame) out for how it works ). 
 
#### USB audio or I2S DAC

If you are using usb audio card or I2S DAC, find the section [player] and follow the instructions there, or select "alsa" in configuration web page.
 
#### WiFi configuration

If you start space window without a network connection and it has hardware capable of it, it will create its own hotspot and then display instructions on the screen how to find it in a browser and configure a connection to an existing network from there. This would work out of the box with pi zero W or with edimax dongles. For the rest of them you may have to change the driver name in the configuration file. This is really handy if you made a space window as a gift to someone and don't know their WiFi details when setting up the machine. 

