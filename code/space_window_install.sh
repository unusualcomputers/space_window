#!/bin/bash
#

# space window
git clone https://github.com/unusualcomputers/space_window.git

# pygame 
apt-get install python-pygame

# radio rough - this installs mopoidy and a bunch of its dependencies
wget https://raw.githubusercontent.com/unusualcomputers/unusualcomputers/master/code/mopidy/mopidyradioroughhtml/rasp_radio_rough_install_lite.sh
chmod a+x ./rasp_radio_rough_install_lite.sh
./rasp_radio_rough_install_lite.sh

# make mopidy server available
sed -i 's|#hostname = 127.0.0.1|hostname=0.0.0.0|g' /root/.config/mopidy/mopidy.conf

# mopidy json client
pip install https://github.com/ismailof/mopidy-json-client/archive/master.zip

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
