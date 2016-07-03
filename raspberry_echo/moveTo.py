#! /bin/bash

apt-get update
apt-get install libasound2-dev memcached python-pip python-alsaaudio vlc -y
#pip install -r requirements.txt
cp initd_alexa.sh /etc/init.d/AlexaPi
update-rc.d AlexaPi defaults
touch /var/log/alexa.log
