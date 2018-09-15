#!/bin/bash
#

apt-get install -y git

# space window
git clone https://github.com/unusualcomputers/space_window.git

# access point stuff
apt-get install -y dnsmasq hostapd
systemctl stop dnsmasq
systemctl stop hostapd
#systemctl disable dnsmasq
#systemctl disable hostapd

# omx player
apt-get install -y omxplayer
# pygame 
apt-get install -y python-pygame

# radio rough - this installs mopidy and a bunch of its dependencies
wget https://raw.githubusercontent.com/unusualcomputers/unusualcomputers/master/code/mopidy/mopidyradioroughhtml/rasp_radio_rough_install_lite.sh
chmod a+x ./rasp_radio_rough_install_lite.sh
./rasp_radio_rough_install_lite.sh

# mopidy json client
pip install https://github.com/ismailof/mopidy-json-client/archive/master.zip

# mopidy musicbox webclient
pip install mopidy-musicbox-webclient

# websocket
pip install websocket-client

# streamlink
pip install streamlink

# pafy
pip install pafy

# jsonpickle
pip install git+https://github.com/jsonpickle/jsonpickle.git

# comic sans
apt-get install -y ttf-mscorefonts-installer

# run mopidy for the first time
sudo mopidy&
sleep 120
sudo pkill -9 mopidy
sleep 5

# make mopidy server available
sed -i 's|#hostname = 127.0.0.1|hostname=0.0.0.0|g' /root/.config/mopidy/mopidy.conf
sed -i "s|#media_dir =|media_dir = $(pwd)/space_window/code/music|" /root/.config/mopidy/mopidy.conf
sed -i "s|#media_dirs =|media_dirs = $(pwd)/space_window/code/music|" /root/.config/mopidy/mopidy.conf
# add the launching code to rc.local
sed -i "\$i sudo mopidy local scan" /etc/rc.local
sed -i "\$i sudo mopidy&" /etc/rc.local
sed -i "\$i sleep 10" /etc/rc.local
sed -i "\$i sudo python $(pwd)/space_window/code/space_window.py&" /etc/rc.local
sed -i '1s/$/ consoleblank=0/' /boot/cmdline.txt

#rng tools help python requests
apt-get install -y rng-tools
systemctl enable rng-tools
systemctl start rng-tools
reboot now

