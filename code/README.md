Space window is like a picture that shows faraway places.

It will stream videos from the internet, or play your own ones, show beautiful pictures of space that NASA publishes every day, play radio and podcasts and show time and weather where you are. It can also be a pretty clock or play a slideshow of your own photos. You control it via an internet browser.

If it is not connected to the internet it will create it's own standalone WiFi network so that you can connect to it via a browser and upload videos, music or photos that it will then play for you. 

Either way, it will be telling you what to do or how to connect to it.

 
## How to use it

Once you connect to the space window you will see something like this in your browser: 

![space window browser](https://github.com/unusualcomputers/space_window/blob/master/pics/sw_browser_home.png)

The list at the top are videos, you can either upload your own or more interestingly just give it links to online streams or you tube clips (even playlists). If your network is very slow you can specify quality of the videos you want to stream.

 * Nasa POD   
   
   Clicking this will connect to Nasa and start a slideshow of their picture of the day, starting with today's one and then going through all the other thousands of them in a random order. 

* Radio
  
   Radio opens a new tab showing [Mopidy](https://www.mopidy.com/) control page. Here world is your oyster - it will play thousands of internet radio stations, podcasts, streams from MixCloud and so on.

* Clock

  With this space window becomes an old fashioned digital clock. It will also tell you about the wheather where you are or where you configure it to - it gets this from wonderful yr.no site and will cover most places in the world.

* Photo Gallery

    A slide show of your own photos, when you click this it will show you the list of them in the browser and let you add more.  

* Play next

    Plays next :)

* Upload video

    You can upload your own videos and subtitles for them.

* Upload music

    If you want mopidy to play your local music files you can upload them here.

* Configuration
    There are quite a few options here, fonts, colors, slideshow speed, location for the clock and weather display and so on. More complicated ones are documented on the configuration page (if you are using a USB sound card or I2S dac you can also configure that here)

The bottom row of buttons is for maintenance, you'll use it rarely if ever, but they are handy (Update most of all, this is how we will fix bugs you tell us about).




## Hardware


Most of the magic is in software and it will run just fine on Pi Zero - a bigger Pi would work of course, though it would be somewhat wasteful. Apart from the computer you will need a screen of some kind, some way for raspberry to reproduce sound would be nice and a connection to internet helps, though even without it picture slideshows, uploaded music and videos would work fine. 

Our first one used nice 10.1'' lcd from banggood, the second one a 4'' Waveshare one [LINK TO rock-i]. The big lcd we used came with a board that had separate 3.5mm audio output so that was easy, we also tried this with an I2S audio DAC and a usb sound card. Finally you'll need a way to connect to the internet. Pi Zero W built in WiFi works well, though in our models we used plain old Pi Zero with a short cable and Edimax WiFi dongle in order to get the dongle out in the clear to improve reception (one thing you want to try and get right is a nice strong WiFi reception). Of course you will need a power supply, how mighty it should be will depend mostly on your choice of the screen, for our big 10'' lcd version we use a 2.5A one.

![sw1](https://github.com/unusualcomputers/space_window/blob/master/pics/space1.jpg) ![sw2](https://github.com/unusualcomputers/space_window/blob/master/pics/space3.jpg)
![sw3](https://github.com/unusualcomputers/space_window/blob/master/pics/space4.jpg)
![swback](https://github.com/unusualcomputers/space_window/blob/master/pics/spaceW%20back1.jpg)


All in all, you need to put together a raspberry based machine that can connect to internet, has a screen on which OMXPlayer can display movies and if you can some way for it to play music. It should all run from a Raspbian Lite installation, window managers would just slow things down and are not used at all. There is so much information and good advice around on how to get this going in various configurations that almost anything you can think of can be made to work. Let us know if you need help figuring any of this out, more than happy to help.


## Installation

To start with you need to install [Raspbian Lite](https://www.raspberrypi.org/downloads/raspbian/) and connect it to the internet (this depends quite a bit on your choice of hardware, but for WiFi [this will work](https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md). It is nice to change the name of your new computer because that is how you will be finding on the network, we called ours SpaceWindow so to get to it we type spacewindow.local in a browser, this is easily done using [raspi-config](https://www.raspberrypi.org/documentation/configuration/raspi-config.md).

You will need to make sure that OMXPlayer works in your setup. There is a simple way to test it here [here](https://www.raspberrypi.org/documentation/raspbian/applications/omxplayer.md), but this will depend entirely on how you hooked things up, drop us a line if you get stuck. Rememebr to check if it can produce sound too.

Once all that is ready and you can connect to your raspberry terminal, download and run [this script](https://raw.githubusercontent.com/unusualcomputers/space_window/master/code/space_window_install.sh), for example:

```
 wget https://raw.githubusercontent.com/unusualcomputers/space_window/master/code/space_window_install.sh
 sudo chmod a+x ./space_window_install.sh
 ./space_window_install.sh
```

The script installs a whole bunch of things, it's pretty easy to read if you want to fid out what, but in short all of it is software used to run our code provided by good people of the internet and nothing else. It takes a while, about half an hour or more on Pi Zero.


## Configuration

Most of this can be done online once the software is running, but there are a few bits you may want to deal with before that. 
All configuration is in a file space_window/code/space_window.conf.

If you are using a GPIO screen you will need a bit of extra magic. Find the section [pygame] in this file. Here you will need to configure fbdev variables. For most screens you just need to set fbdev to /dev/fb1 and then the screen size and color depth (check [this](https://github.com/notro/fbtft/wiki/Pygame) out for how it works ). 
 
If you are using usb audio card or I2S DAC, find the section [player] and follow the instructions there.

The rest of it you can sort out once it's up and running via your browser, much easier.

Then reboot and watch the screen, it will tell you how to connect to it (basically type in the_name_of_your_machine.local in a browser on some computer on the same network, default is rapberrypi.local, ours is spacewindow.local).  
 

